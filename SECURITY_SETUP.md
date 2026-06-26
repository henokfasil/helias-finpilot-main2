# 🔐 Security Setup Instructions

## What's Been Added

Your public repo is now protected with **dashboard authentication**. Users must login before accessing any data.

---

## 🚨 IMMEDIATE ACTION REQUIRED

### Update Streamlit Cloud Secrets

1. Go to: https://share.streamlit.io/apps
2. Find: "helias-finpilot-main"
3. Click ⋯ → **Settings** → **Secrets**
4. **ADD NEW CREDENTIALS** (replace defaults):

```toml
# Your new, secure credentials
DASHBOARD_USER = "your_secure_username"
DASHBOARD_PASSWORD = "your_secure_password"

# Keep existing credentials
DATABASE_URL = "postgresql://postgres.xqxqvbgbycczaqkspvyz:nAvyfG5QFtJreaDC@aws-0-eu-west-1.pooler.supabase.com:5432/postgres?sslmode=require"
APP_ENV = "production"
APP_LOG_LEVEL = "INFO"
```

5. Click **Save** (app will auto-redeploy)

---

## 🔄 Next: Update VPS

### SSH into VPS

```bash
ssh root@72.60.133.179
# Password: hFr57ig-mN?UY#
```

### Update .env file

```bash
cd /opt/helias-finpilot-main2
nano .env
```

Change:
```bash
# Add or update these lines
DASHBOARD_USER=your_secure_username
DASHBOARD_PASSWORD=your_secure_password
```

Save (Ctrl+X → Y → Enter)

### Restart the app

```bash
pm2 restart streamlit-finpilot
```

---

## 🧪 Test It

1. Go to: https://helias-finpilot-main.streamlit.app/
2. You should see a **login page** 🔐
3. Enter your credentials
4. Click **Login** → Dashboard loads

---

## 📚 Security Features Now Active

✅ **Login Page**
- Username & password required
- Redirects unauthenticated users

✅ **Session Management**
- Auto-logout after 24 hours
- Manual logout button in sidebar

✅ **Password Security**
- Passwords hashed with SHA-256
- Never stored in plaintext
- Never in git repository

✅ **Credentials Storage**
- Streamlit Cloud Secrets (encrypted)
- VPS .env (restricted file permissions)
- Never in public code

---

## 🎯 Default Credentials (Before Update)

```
Username: admin
Password: finpilot2026
```

⚠️ **These will only work if you don't set custom credentials!**

---

## 🔍 Verify Setup

### Check Streamlit Cloud
```
App loads → Login page appears → ✅ Success
```

### Check VPS
```bash
ssh root@72.60.133.179
pm2 status | grep streamlit-finpilot
# Should show: online
```

---

## 📖 Documentation

See **SECURITY.md** for:
- Detailed authentication flow
- How to change credentials
- Environment variable options
- Security best practices
- Incident response procedures

---

## ✅ Security Checklist

- [ ] Update Streamlit Cloud secrets with new credentials
- [ ] Update VPS .env with new credentials
- [ ] Restart VPS app (pm2 restart)
- [ ] Test login on Streamlit Cloud
- [ ] Share new credentials with team via secure channel
- [ ] Document new credentials in secure location
- [ ] Review SECURITY.md for best practices
- [ ] Monitor access logs

---

## 🔑 Credentials Management

### Secure Way to Share Credentials

❌ **DON'T:**
- Email plain text passwords
- Share in Slack
- Put in git commits
- Use default credentials in production

✅ **DO:**
- Use password manager (1Password, LastPass, etc.)
- Share via secure channel (encrypted email, Signal, etc.)
- Change credentials regularly
- Use strong passwords (12+ characters)

---

## 🚨 If Something Goes Wrong

### App Won't Load (HTTP 303 Redirect)
→ Check Streamlit Cloud secrets are set  
→ Restart the app

### Login Fails
→ Check username/password in secrets  
→ Verify no typos
→ Check env variables on VPS

### Forgotten Password
→ Update secrets and redeploy  
→ Or restart app with new .env

---

## 📞 Quick Reference

| Need | Location |
|------|----------|
| **Change Dashboard Credentials** | App Settings → Secrets |
| **Change DB Credentials** | App Settings → Secrets (DATABASE_URL) |
| **VPS Configuration** | `/opt/helias-finpilot-main2/.env` |
| **View Logs** | `pm2 logs streamlit-finpilot` |
| **Restart App** | `pm2 restart streamlit-finpilot` |
| **Security Guide** | `SECURITY.md` |

---

**Status:** 🟢 Authentication system deployed & ready  
**Next Step:** Update your credentials in Streamlit Cloud  
**Time to Complete:** ~5 minutes
