# GitHub Push & Render Deployment Instructions

## Step 1: Create GitHub Personal Access Token

Since HTTPS authentication requires authentication, follow these steps:

### On GitHub:
1. Go to https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Set token name: `AI-Portal-Automation`
4. Select scopes:
   - ✅ `repo` (full control of private repositories)
   - ✅ `workflow` (update GitHub Action workflows)
5. Click **"Generate token"**
6. **Copy the token** (you won't see it again!)

### On Your Machine:
1. Open PowerShell/Terminal
2. Configure Git credentials:
   ```bash
   cd "c:\Users\hp\Desktop\AI AUTOMATION FOR PMJAY"
   git config --global credential.helper manager-core
   ```
3. Push code:
   ```bash
   git push -u origin main
   ```
4. When prompted for credentials:
   - **Username**: `durveshparab12345`
   - **Password**: Paste the token you copied above

---

## Alternative: Use SSH Key

If you prefer SSH (more secure):

### Generate SSH Key:
```bash
ssh-keygen -t ed25519 -C "durvesh@example.com"
# Just press Enter for all prompts
```

### Add SSH Key to GitHub:
1. Copy your public key:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
2. Go to https://github.com/settings/keys
3. Click **"New SSH key"**
4. Paste the key
5. Click **"Add SSH key"**

### Update Git Remote (use SSH):
```bash
cd "c:\Users\hp\Desktop\AI AUTOMATION FOR PMJAY"
git remote remove origin
git remote add origin git@github.com:durveshparab12345-cpu/AI-AUTOMATION-FOR-GOVERNMENT-PORTAL.git
git push -u origin main
```

---

## Step 2: Verify Code is on GitHub

1. Go to: https://github.com/durveshparab12345-cpu/AI-AUTOMATION-FOR-GOVERNMENT-PORTAL
2. You should see all your code files
3. Check that latest commit is visible in commit history

---

## Step 3: Deploy on Render

### 3.1 Create Render Account
- Go to https://render.com
- Sign up with GitHub account (recommended)
- Click "GitHub" during signup → Authorize

### 3.2 Deploy Backend

1. In Render dashboard: **New** → **Web Service**
2. Select your repository: `AI-AUTOMATION-FOR-GOVERNMENT-PORTAL`
3. Configure:
   - **Name**: `ai-portal-backend`
   - **Environment**: Python 3.10
   - **Build Command**:
     ```bash
     cd backend && pip install -r requirements.txt && python -m alembic upgrade head
     ```
   - **Start Command**:
     ```bash
     cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: Free

4. Add environment variables:
   | Key | Value |
   |-----|-------|
   | `APP_ENV` | `production` |
   | `DEBUG` | `false` |
   | `SECRET_KEY` | Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
   | `CORS_ORIGINS` | `*` (for now, restrict later) |
   | `DEMO_MODE` | `false` |

5. Click **"Create Web Service"**
6. Wait 5-10 minutes for build
7. Copy the URL (e.g., `https://ai-portal-backend.onrender.com`)

### 3.3 Create PostgreSQL Database

1. In Render: **New** → **PostgreSQL**
2. Configure:
   - **Name**: `ai-portal-db`
   - **Database**: `ai_portal_prod`
   - **User**: `postgres`
   - **Plan**: Free

3. Click **"Create Database"**
4. Copy the **Internal Database URL** (from database details)

### 3.4 Update Backend with Database

1. Go to backend service → **Environment**
2. Add variable:
   - **Key**: `DATABASE_URL`
   - **Value**: Paste the URL from step 3.3
3. Click **"Save"**
4. Service will redeploy automatically
5. Check deploy logs to verify migrations ran

### 3.5 Deploy Frontend

1. **New** → **Web Service** → Select repository
2. Configure:
   - **Name**: `ai-portal-frontend`
   - **Environment**: Node 18
   - **Build Command**:
     ```bash
     cd frontend && npm install && npm run build
     ```
   - **Start Command**:
     ```bash
     cd frontend && npm run preview -- --host 0.0.0.0
     ```
   - **Plan**: Free

3. Add environment variables:
   | Key | Value |
   |-----|-------|
   | `VITE_API_BASE_URL` | `https://ai-portal-backend.onrender.com/api/v1` |
   | `VITE_APP_NAME` | `AI Portal Automation` |

4. Click **"Create Web Service"**
5. Wait for build
6. Copy frontend URL (e.g., `https://ai-portal-frontend.onrender.com`)

### 3.6 Update Backend CORS

1. Backend service → **Environment**
2. Update `CORS_ORIGINS`:
   ```
   https://ai-portal-frontend.onrender.com
   ```
3. Click **"Save"** → Redeploy

---

## Step 4: Test Deployment

1. Open frontend: https://ai-portal-frontend.onrender.com
2. Login with:
   - Email: `demo@ai-portal-demo.local`
   - Password: `DemoPassword@2026`
3. Navigate through pages
4. Test API at: https://ai-portal-backend.onrender.com/docs

---

## Troubleshooting

### GitHub Push Fails
- Verify personal access token is correct
- Ensure you copied entire token
- Check username is `durveshparab12345`

### Render Build Fails
- Check build logs in Render dashboard
- Common issues:
  - Python version incompatibility
  - Missing dependencies in `requirements.txt`
  - Node version issues

### Database Connection Fails
- Verify `DATABASE_URL` is complete
- Check internal URL (not public URL)
- Ensure URL format: `postgresql+asyncpg://...`

### Frontend Shows API Errors
- Verify backend is running (check logs)
- Confirm `VITE_API_BASE_URL` in frontend environment
- Check CORS settings in backend

---

## Environment Variables - Complete Reference

### Backend Production (.env on Render)
```
APP_NAME=AI Portal Automation Platform
APP_ENV=production
DEBUG=false
SECRET_KEY=<strong-random-key>
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
REDIS_URL=redis://default:password@host:port
CORS_ORIGINS=https://ai-portal-frontend.onrender.com
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DEMO_MODE=false
```

### Frontend Production (.env on Render)
```
VITE_API_BASE_URL=https://ai-portal-backend.onrender.com/api/v1
VITE_APP_NAME=AI Portal Automation
VITE_APP_VERSION=0.2.0
```

---

## Final URLs (After Deployment)

- **Frontend**: https://ai-portal-frontend.onrender.com
- **Backend**: https://ai-portal-backend.onrender.com
- **API Docs**: https://ai-portal-backend.onrender.com/docs
- **Health Check**: https://ai-portal-backend.onrender.com/api/v1/health

---

## Next Steps

1. ✅ Create Personal Access Token
2. ✅ Push code to GitHub
3. ✅ Deploy backend on Render
4. ✅ Deploy database on Render
5. ✅ Deploy frontend on Render
6. ✅ Test all features
7. ⏭️ (Optional) Configure custom domain
8. ⏭️ (Optional) Set up CI/CD auto-deployment

---

## Need Help?

- **Render Support**: https://render.com/docs
- **GitHub Help**: https://docs.github.com
- **Backend Issues**: Check `/backend/app/main.py` and logs
- **Frontend Issues**: Check browser console and network tab

