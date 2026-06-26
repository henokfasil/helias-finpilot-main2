# Quick Start — Helias FinPilot Dashboard

## ✅ Fixed Issues
The Supabase connection pooling and Streamlit integration has been fixed. The app now:
- ✅ Handles database connections gracefully with proper pooling
- ✅ Won't crash on connection errors
- ✅ Works with both local SQLite and cloud Supabase
- ✅ Automatically validates connections before use

## 📋 Prerequisites
- Python 3.8+
- pip or poetry
- Git (already done ✓)

## 🚀 Quick Start

### 1. **Install Dependencies** (first time only)
```bash
pip install -r requirements.txt
```

### 2. **Setup Environment**

**Option A: Local Development (SQLite)**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and keep the default SQLite path:
# DATABASE_URL=sqlite:///./finpilot.db

# This is the default, so you don't need to change anything
```

**Option B: Production (Supabase PostgreSQL)**
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your Supabase credentials:
DATABASE_URL=postgresql://[user]:[password]@[host]:5432/[database]

# For Streamlit Cloud: Go to App Settings → Secrets and add the DATABASE_URL there
```

### 3. **Run the Dashboard**
```bash
streamlit run dashboard/app.py
```

The app will start at `http://localhost:8501`

## 📊 Features
- 📈 Financial Overview with KPIs
- 💳 Transactions Management
- 📄 Reports Generation
- 📎 Receipt Management
- ⚙️ Settings

## 🔍 Troubleshooting

### "Database Error: server closed the connection..."
✅ **FIXED** — The app now handles connection errors gracefully. You'll see a friendly error message instead of a crash.

### "Connection timeout"
- Increase the `connect_timeout` in `dashboard/db.py` if using a slow network
- Check your internet connection
- Verify your DATABASE_URL is correct

### "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### SQLite file not created
```bash
# The finpilot.db will be created automatically in the first run
# If needed, you can create it manually:
touch finpilot.db
```

## 📱 Streamlit Cloud Deployment

1. **Push to GitHub** (already done ✓)
2. **Connect to Streamlit Cloud**:
   - Go to [streamlit.io](https://streamlit.io)
   - Click "New app"
   - Select this repository
   - Choose `dashboard/app.py` as the main file
3. **Configure Secrets**:
   - Go to App Settings → Secrets
   - Add your `DATABASE_URL` from Supabase:
   ```toml
   DATABASE_URL = "postgresql://user:password@host:5432/database"
   ```
4. **Deploy** — Streamlit will automatically deploy after each git push

## 📚 Documentation
- See `SUPABASE_STREAMLIT_FIXES.md` for technical details on the fixes
- See `DEPLOYMENT_GUIDE.md` for production deployment

## 🆘 Need Help?
- Check the logs: `streamlit run dashboard/app.py` will show detailed errors
- Review `SUPABASE_STREAMLIT_FIXES.md` for connection pooling details
- Check your environment variables are correctly set

---
**Ready to go!** Run `streamlit run dashboard/app.py` now. 🚀
