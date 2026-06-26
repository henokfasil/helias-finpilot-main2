"""
Authentication module for FinPilot Dashboard
Provides session-based authentication without storing passwords
"""
import streamlit as st
import hashlib
from datetime import datetime, timedelta
import os

# Default credentials (can be overridden with env variables)
DEFAULT_USERNAME = os.getenv("DASHBOARD_USER", "admin")
DEFAULT_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "finpilot2026")

# Hash the password for comparison (not storing plaintext)
def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(password: str, stored_hash: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == stored_hash

def init_auth_session():
    """Initialize session state for authentication"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "login_time" not in st.session_state:
        st.session_state.login_time = None

def require_authentication():
    """
    Display login form and verify credentials.
    Returns True if user is authenticated, False otherwise.
    """
    init_auth_session()

    if st.session_state.authenticated:
        # Check session timeout (24 hours)
        if st.session_state.login_time:
            elapsed = datetime.now() - st.session_state.login_time
            if elapsed > timedelta(hours=24):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.rerun()
        return True

    # Display login form
    st.set_page_config(
        page_title="FinPilot Login",
        page_icon="🔐",
        layout="centered"
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 🔐 FinPilot Dashboard")
        st.markdown("---")

        username = st.text_input("Username", key="login_username", placeholder="Enter username")
        password = st.text_input("Password", type="password", key="login_password", placeholder="Enter password")

        col_login, col_demo = st.columns(2)

        with col_login:
            if st.button("🔓 Login", use_container_width=True, type="primary"):
                # Verify credentials
                password_hash = os.getenv("DASHBOARD_PASSWORD_HASH", hash_password(DEFAULT_PASSWORD))

                if username == DEFAULT_USERNAME and check_password(password, password_hash):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.login_time = datetime.now()
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")

        with col_demo:
            st.caption("Demo credentials available")

        st.markdown("---")
        st.caption("🔒 Your login session expires after 24 hours")

    return False

def logout():
    """Logout the user"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.login_time = None
    st.rerun()

def show_user_info():
    """Display user info and logout button in sidebar"""
    if st.session_state.authenticated:
        with st.sidebar:
            st.divider()
            col1, col2 = st.columns([2, 1])
            with col1:
                st.caption(f"👤 Logged in as: **{st.session_state.username}**")
            with col2:
                if st.button("🚪 Logout", use_container_width=True):
                    logout()
