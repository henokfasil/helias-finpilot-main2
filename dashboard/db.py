"""
Dashboard database helpers — read-only queries returning pandas DataFrames.
Uses Supabase PostgreSQL (production) or SQLite (local dev).

Functions:
  load_transactions()      — all transactions with category/counterparty
  load_attachments()       — receipt files
  load_categories()        — active categories
  load_company()           — company info dict
  load_tax_data()          — confirmed transactions with tax fields
  load_financial_data()    — confirmed transactions with activity_type (for financial statements)
  load_account_snapshots() — manual Balance Sheet entries (account_snapshots table)
  load_reports()           — saved generated reports
"""
from __future__ import annotations

import sys
import os
from pathlib import Path

# Ensure project root is on the path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

print("=" * 80)
print("DB.PY LOADING - Checking secrets...")

import pandas as pd
import streamlit as st

print(f"Streamlit secrets keys: {list(st.secrets.keys()) if hasattr(st.secrets, 'keys') else 'NO SECRETS'}")

from sqlalchemy import create_engine, text, pool
from sqlalchemy.pool import QueuePool, StaticPool

from app.config import settings
print("=" * 80)


def _get_database_url() -> str:
    """
    Prefer Streamlit Cloud secrets, fall back to .env / default.
    On Streamlit Cloud, secrets are injected via st.secrets.
    """
    try:
        url = st.secrets["DATABASE_URL"]
        print(f"DEBUG: Using DATABASE_URL from secrets: {url[:80]}...")
        return url
    except (KeyError, FileNotFoundError):
        url = settings.database_url
        print(f"DEBUG: Using DATABASE_URL from settings: {url[:80]}...")
        return url


@st.cache_resource
def get_engine():
    """
    Single shared engine for the dashboard (read-only).
    Properly configured for Supabase PostgreSQL or local SQLite.
    """
    db_url = _get_database_url()
    print(f"DEBUG: Creating engine with URL: {db_url[:80]}...")

    if "sqlite" in db_url:
        # SQLite: use StaticPool for local development
        engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        # PostgreSQL/Supabase: use QueuePool with optimized settings
        engine = create_engine(
            db_url,
            poolclass=QueuePool,
            pool_size=5,                    # Reduce pool size for Supabase limits
            max_overflow=2,                 # Allow temporary connections if needed
            pool_pre_ping=True,             # Test connections before use (prevents stale connection errors)
            pool_recycle=3600,              # Recycle connections after 1 hour
            connect_args={
                "connect_timeout": 10,      # 10 second connection timeout
            },
        )

    print("DEBUG: Engine created successfully")
    return engine


def _execute_query_safe(engine, sql, params=None, as_dataframe=True):
    """Safely execute a database query with error handling."""
    try:
        with engine.connect() as conn:
            if as_dataframe:
                return pd.read_sql(sql, conn, params=params)
            else:
                row = conn.execute(sql, params or {}).fetchone()
                return dict(row._mapping) if row else {}
    except Exception as e:
        print(f"ERROR in query execution: {e}")
        st.error(f"Database connection error: {str(e)[:100]}")
        return pd.DataFrame() if as_dataframe else {}


@st.cache_data(ttl=30)
def load_transactions(company_id: int = 1) -> pd.DataFrame:
    engine = get_engine()
    sql = text("""
        SELECT
            t.id,
            t.transaction_date,
            t.transaction_date_et,
            t.transaction_type,
            t.amount,
            t.currency,
            t.description,
            t.payment_method,
            t.reference_number,
            t.status,
            t.ai_confidence,
            t.raw_text,
            t.created_at,
            c.name  AS category,
            cp.name AS counterparty
        FROM transactions t
        LEFT JOIN categories    c  ON t.category_id    = c.id
        LEFT JOIN counterparties cp ON t.counterparty_id = cp.id
        WHERE t.company_id = :cid
        ORDER BY t.transaction_date DESC, t.id DESC
    """)
    try:
        with engine.connect() as conn:
            df = pd.read_sql(sql, conn, params={"cid": company_id})
        df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        return df
    except Exception as e:
        print(f"ERROR loading transactions: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=30)
def load_attachments(company_id: int = 1) -> pd.DataFrame:
    engine = get_engine()
    sql = text("""
        SELECT
            a.id,
            a.original_filename,
            a.stored_path,
            a.file_type,
            a.file_size_bytes,
            a.created_at,
            a.transaction_id,
            t.transaction_date,
            t.amount,
            t.currency,
            cp.name AS counterparty
        FROM attachments a
        LEFT JOIN transactions   t  ON a.transaction_id = t.id
        LEFT JOIN counterparties cp ON t.counterparty_id = cp.id
        WHERE a.company_id = :cid
        ORDER BY a.created_at DESC
    """)
    try:
        with engine.connect() as conn:
            df = pd.read_sql(sql, conn, params={"cid": company_id})
        if not df.empty:
            df["created_at"] = pd.to_datetime(df["created_at"])
            df["transaction_date"] = pd.to_datetime(df["transaction_date"])
            df["file_size_kb"] = (df["file_size_bytes"] / 1024).round(1)
        return df
    except Exception as e:
        print(f"ERROR loading attachments: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=30)
def load_categories(company_id: int = 1) -> pd.DataFrame:
    engine = get_engine()
    sql = text("""
        SELECT id, name, type, is_active
        FROM categories
        WHERE company_id = :cid
        ORDER BY type, name
    """)
    try:
        with engine.connect() as conn:
            return pd.read_sql(sql, conn, params={"cid": company_id})
    except Exception as e:
        print(f"ERROR loading categories: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=30)
def load_company(company_id: int = 1) -> dict:
    engine = get_engine()
    sql = text("SELECT * FROM companies WHERE id = :cid LIMIT 1")
    try:
        with engine.connect() as conn:
            row = conn.execute(sql, {"cid": company_id}).fetchone()
        return dict(row._mapping) if row else {}
    except Exception as e:
        print(f"ERROR loading company {company_id}: {e}")
        st.error(f"Failed to load company data: {str(e)[:100]}")
        return {}


@st.cache_data(ttl=30)
def load_tax_data(company_id: int = 1) -> pd.DataFrame:
    """Load all confirmed transactions with tax fields for the Tax dashboard."""
    engine = get_engine()
    sql = text("""
        SELECT
            t.id,
            t.transaction_date,
            t.transaction_type,
            t.amount,
            t.currency,
            t.vat_amount,
            t.withholding_tax,
            t.is_vat_inclusive,
            t.is_tax_relevant,
            t.description,
            t.status,
            cp.name AS counterparty
        FROM transactions t
        LEFT JOIN counterparties cp ON t.counterparty_id = cp.id
        WHERE t.company_id = :cid
          AND t.status = 'confirmed'
        ORDER BY t.transaction_date DESC
    """)
    try:
        with engine.connect() as conn:
            df = pd.read_sql(sql, conn, params={"cid": company_id})
        if not df.empty:
            df["transaction_date"] = pd.to_datetime(df["transaction_date"])
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
            df["vat_amount"] = pd.to_numeric(df["vat_amount"], errors="coerce").fillna(0)
            df["withholding_tax"] = pd.to_numeric(df["withholding_tax"], errors="coerce").fillna(0)
        return df
    except Exception as e:
        print(f"ERROR loading tax data: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=30)
def load_financial_data(company_id: int = 1) -> pd.DataFrame:
    """
    Load all confirmed transactions with activity_type for financial statements.
    Includes category name and counterparty name.
    """
    engine = get_engine()
    sql = text("""
        SELECT
            t.id,
            t.transaction_date,
            t.transaction_type,
            t.activity_type,
            t.amount,
            t.currency,
            t.description,
            t.payment_method,
            t.vat_amount,
            t.withholding_tax,
            t.is_vat_inclusive,
            t.status,
            c.name  AS category,
            cp.name AS counterparty
        FROM transactions t
        LEFT JOIN categories     c  ON t.category_id     = c.id
        LEFT JOIN counterparties cp ON t.counterparty_id = cp.id
        WHERE t.company_id = :cid
          AND t.status = 'confirmed'
        ORDER BY t.transaction_date ASC, t.id ASC
    """)
    try:
        with engine.connect() as conn:
            df = pd.read_sql(sql, conn, params={"cid": company_id})
        df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
        df["vat_amount"] = pd.to_numeric(df["vat_amount"], errors="coerce").fillna(0)
        df["withholding_tax"] = pd.to_numeric(df["withholding_tax"], errors="coerce").fillna(0)
        df["activity_type"] = df["activity_type"].fillna("operating")
        return df
    except Exception as e:
        print(f"ERROR loading financial data: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=30)
def load_account_snapshots(company_id: int = 1) -> pd.DataFrame:
    """Load manually-entered Balance Sheet items (AccountSnapshot)."""
    engine = get_engine()
    sql = text("""
        SELECT id, account_name, account_type, account_subtype,
               amount, currency, entry_date, notes, is_active
        FROM account_snapshots
        WHERE company_id = :cid
          AND is_active = true
        ORDER BY account_type, account_name
    """)
    try:
        with engine.connect() as conn:
            df = pd.read_sql(sql, conn, params={"cid": company_id})
        if not df.empty:
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
            df["entry_date"] = pd.to_datetime(df["entry_date"], errors="coerce")
        return df
    except Exception as e:
        print(f"ERROR loading account snapshots: {e}")
        return pd.DataFrame()


def delete_transactions(ids: list[int], company_id: int = 1) -> int:
    """
    Delete transactions by ID list. Only deletes rows belonging to company_id.
    Returns the number of rows actually deleted.
    """
    if not ids:
        return 0
    engine = get_engine()
    sql = text("""
        DELETE FROM transactions
        WHERE id = ANY(:ids) AND company_id = :cid
    """)
    try:
        with engine.begin() as conn:
            result = conn.execute(sql, {"ids": ids, "cid": company_id})
        st.cache_data.clear()
        return result.rowcount
    except Exception as e:
        print(f"ERROR deleting transactions: {e}")
        st.error(f"Failed to delete transactions: {str(e)[:100]}")
        return 0


@st.cache_data(ttl=30)
def load_reports(company_id: int = 1) -> pd.DataFrame:
    engine = get_engine()
    sql = text("""
        SELECT id, report_type, period_year, period_month, content, created_at
        FROM reports
        WHERE company_id = :cid
        ORDER BY period_year DESC, period_month DESC
    """)
    try:
        with engine.connect() as conn:
            df = pd.read_sql(sql, conn, params={"cid": company_id})
        return df
    except Exception as e:
        print(f"ERROR loading reports: {e}")
        return pd.DataFrame()
