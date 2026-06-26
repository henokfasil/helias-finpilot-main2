# Security Guide — Helias FinPilot

## 🔐 Dashboard Authentication

Your Streamlit dashboard now includes **session-based authentication** to protect from unauthorized access.

### Login Credentials

**Default Credentials:**
```
Username: admin
Password: finpilot2026
```

⚠️ **Change these immediately in production!**

### Custom Credentials

#### Option 1: Environment Variables (Recommended)

Set these before running the app:

```bash
# Linux/Mac
export DASHBOARD_USER="your_username"
export DASHBOARD_PASSWORD="your_secure_password"
streamlit run dashboard/app.py

# Or in .env file
DASHBOARD_USER=your_username
DASHBOARD_PASSWORD=your_secure_password
```

#### Option 2: Streamlit Cloud Secrets

Go to **App Settings → Secrets** and add:

```toml
DASHBOARD_USER = "your_username"
DASHBOARD_PASSWORD = "your_secure_password"
```

#### Option 3: Advanced - Password Hash

For extra security, pre-hash your password:

```python
import hashlib
password = "your_secure_password"
password_hash = hashlib.sha256(password.encode()).hexdigest()
print(password_hash)
```

Then set environment variable:
```bash
export DASHBOARD_PASSWORD_HASH="your_hash_here"
```

### Session Management

- **Session Timeout:** 24 hours
- **Session Storage:** Browser (Streamlit session state)
- **Auto-Logout:** After 24 hours of login
- **Manual Logout:** Click "🚪 Logout" button in sidebar

---

## 🔒 Database Credentials

**NEVER commit database credentials to the repository!**

### Current Setup

✅ **DATABASE_URL stored in:**
- Streamlit Cloud Secrets (primary)
- VPS `.env` file (restricted permissions)
- Never in git repository

### Supabase Credentials

| Item | Status | Location |
|------|--------|----------|
| Connection String | 🔒 Secure | Streamlit Secrets |
| Password | 🔒 Secure | .env (not in repo) |
| Project URL | ✅ Public | OK to share |
| Project ID | ✅ Public | OK to share |

### Accessing Credentials

**Streamlit Cloud:**
```
App Settings → Secrets → DATABASE_URL
```

**VPS:**
```bash
ssh root@72.60.133.179
cat /opt/helias-finpilot-main2/.env
# Only accessible to root
```

---

## 📁 Repository Security

### What's Protected ✅

- ❌ No `DATABASE_URL` in code
- ❌ No passwords in code
- ❌ No API keys in code
- ✅ `.env.example` with placeholders only

### What's Public 🌐

- ✅ Source code (safe to share)
- ✅ Documentation
- ✅ Configuration templates
- ✅ Supabase project ID (not sensitive)

### Best Practices

1. **Never commit secrets**
   ```bash
   # ❌ DON'T
   git add .env
   
   # ✅ DO
   git add .env.example
   ```

2. **Use `.gitignore`**
   ```
   .env
   .env.local
   *.pem
   *.key
   secrets/
   ```

3. **Review before pushing**
   ```bash
   git diff --staged  # Check what you're committing
   ```

---

## 🛡️ Authentication Flow

```
User Access
    ↓
Login Page Displayed
    ↓
Username & Password Entered
    ↓
Password Hashed & Verified
    ↓
Session Created (24h timeout)
    ↓
Dashboard Accessible
    ↓
User Logout or Timeout
    ↓
Session Cleared
```

### Implementation Details

**File:** `dashboard/auth.py`

Key functions:
- `require_authentication()` - Enforce login
- `hash_password()` - SHA-256 hashing
- `check_password()` - Verify credentials
- `show_user_info()` - Display user in sidebar
- `logout()` - Clear session

**File:** `dashboard/app.py`

Integration:
```python
# Check authentication before loading app
if not require_authentication():
    st.stop()  # Stop execution if not authenticated
```

---

## 🔄 Changing Credentials

### Streamlit Cloud

1. Go to https://share.streamlit.io/apps
2. Find "helias-finpilot-main"
3. Click ⋯ → Settings → Secrets
4. Update `DASHBOARD_USER` and `DASHBOARD_PASSWORD`
5. Click Save (auto-redeploy)

### VPS

```bash
ssh root@72.60.133.179
cd /opt/helias-finpilot-main2

# Edit .env
nano .env
# Update DASHBOARD_USER and DASHBOARD_PASSWORD

# Restart app
pm2 restart streamlit-finpilot
```

### Local Development

```bash
# Create .env
cp .env.example .env

# Edit with your credentials
DASHBOARD_USER=your_username
DASHBOARD_PASSWORD=your_password

# Run app
streamlit run dashboard/app.py
```

---

## 🚨 Security Incidents

### If Credentials Are Compromised

1. **Immediately change credentials:**
   - Update DASHBOARD_USER
   - Update DASHBOARD_PASSWORD
   - Update Supabase password

2. **Check logs for unauthorized access:**
   ```bash
   # Streamlit Cloud logs
   App Settings → Logs
   
   # VPS logs
   pm2 logs streamlit-finpilot
   ```

3. **Invalidate old sessions:**
   - Restart the app (clears all sessions)
   ```bash
   pm2 restart streamlit-finpilot
   ```

4. **Notify team members**
   - Share new credentials via secure channel
   - Update documentation

### If Repository Is Compromised

1. **Rotate all credentials:**
   - Supabase password
   - Dashboard credentials
   - Any API keys

2. **Review git history:**
   ```bash
   git log --oneline
   git log --all -p | grep -i "password\|token\|key"
   ```

3. **Use git filter-branch to remove from history:**
   ```bash
   # Only if sensitive data was committed
   git filter-branch --tree-filter 'rm -f .env' HEAD
   ```

---

## 🔍 Monitoring & Auditing

### Login Attempts

Currently not logged (stateless). To add logging:

1. **Create a simple login audit log:**
   ```python
   # In auth.py
   import json
   from datetime import datetime
   
   def log_login(username, success):
       log_entry = {
           "timestamp": datetime.now().isoformat(),
           "username": username,
           "success": success
       }
       # Append to audit.log file
   ```

2. **Monitor suspicious patterns:**
   - Multiple failed attempts
   - Unusual access times
   - Unusual IP addresses

### Database Access

Supabase provides:
- **Query logs** in Supabase dashboard
- **Connection monitoring**
- **Rate limiting**

---

## 🛠️ Security Configuration

### Environment Variables

```bash
# Dashboard Authentication
DASHBOARD_USER=admin
DASHBOARD_PASSWORD=finpilot2026
# or
DASHBOARD_PASSWORD_HASH=sha256_hash

# Database
DATABASE_URL=postgresql://...

# Application
APP_ENV=production
APP_LOG_LEVEL=INFO
```

### File Permissions

**VPS:**
```bash
# .env should be readable only by app owner
chmod 600 /opt/helias-finpilot-main2/.env

# Check permissions
ls -la /opt/helias-finpilot-main2/.env
# Should show: -rw------- (600)
```

---

## 📋 Security Checklist

- [x] Authentication required for dashboard access
- [x] Database URL stored in secrets (not in code)
- [x] Default credentials documented
- [x] Session timeout configured (24h)
- [x] Password hashing implemented
- [x] HTTPS enforced (Streamlit Cloud)
- [x] SSL required for Supabase connection
- [x] .env excluded from git
- [x] Security guide created
- [ ] Audit logging implemented (optional enhancement)
- [ ] Rate limiting configured (optional enhancement)
- [ ] 2FA for admin account (optional enhancement)

---

## 📚 Resources

- **Streamlit Security:** https://docs.streamlit.io/knowledge-base/using-streamlit/secure-file-uploads
- **Supabase Security:** https://supabase.com/docs/guides/auth
- **OWASP Top 10:** https://owasp.org/www-project-top-ten/

---

## 🔐 Security Tips

1. **Use strong passwords**
   - Minimum 12 characters
   - Mix of uppercase, lowercase, numbers, symbols
   - Avoid dictionary words

2. **Rotate credentials periodically**
   - Every 90 days recommended
   - Immediately if compromised
   - Before onboarding new team members

3. **Monitor access logs**
   - Check for unusual patterns
   - Review failed login attempts
   - Track data access

4. **Keep dependencies updated**
   ```bash
   pip install -U streamlit sqlalchemy psycopg2-binary
   ```

5. **Use VPN for VPS access**
   ```bash
   ssh -i key.pem root@72.60.133.179
   ```

---

**Last Updated:** 2026-06-26  
**Security Level:** 🟢 Moderate (Authentication + Secrets Management)  
**Next Step:** Add audit logging for login attempts
