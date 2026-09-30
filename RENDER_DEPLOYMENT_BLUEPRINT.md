# Render Deployment Blueprint

**Status**: Code pushed to GitHub ✅  
**Next**: Deploy using this blueprint  
**GitHub Repository**: https://github.com/durveshparab12345-cpu/AI-AUTOMATION-FOR-GOVERNMENT-PORTAL  

---

## Deployment Architecture

```
                            Render Services
                            
    ┌─────────────────────────────────────────────────────┐
    │                                                       │
    │  1. PostgreSQL Database (ai-portal-db)              │
    │     • Free tier, 256MB storage                      │
    │     • Connections: Backend                          │
    │                                                       │
    │  2. Backend API (ai-portal-backend)                 │
    │     • FastAPI, Python 3.10                          │
    │     • Connections: Frontend, Database               │
    │                                                       │
    │  3. Frontend Web (ai-portal-frontend)               │
    │     • React + Vite, Node 18                         │
    │     • Connections: Backend API                      │
    │                                                       │
    └─────────────────────────────────────────────────────┘
```

---

## Prerequisites

- ✅ GitHub account: durveshparab12345
- ✅ Code pushed to GitHub
- ⏳ Render account: https://render.com (need to create)

---

## Step 1: Create Render Account

1. Go to: https://render.com
2. Click: "Get Started"
3. Sign up using GitHub account (recommended)
4. Authorize Render to access your GitHub repositories
5. Complete signup

---

## Step 2: Create PostgreSQL Database

1. **In Render Dashboard**:
   - Click: "New +" button
   - Select: "PostgreSQL"

2. **Configure**:
   - Name: `ai-portal-db`
   - Database: `ai_portal_prod`
   - User: `postgres` (default)
   - Plan: **Free**
   - Region: Choose closest to you

3. **Create**:
   - Click: "Create Database"
   - Wait for initialization (~2 minutes)

4. **Save Connection String**:
   - Copy the "Internal Database URL"
   - Format: `postgresql+asyncpg://user:password@host:5432/db`
   - You'll need this for the backend

---

## Step 3: Deploy Backend Service

1. **In Render Dashboard**:
   - Click: "New +" button
   - Select: "Web Service"

2. **Connect Repository**:
   - Select: "GitHub"
   - Repository: `AI-AUTOMATION-FOR-GOVERNMENT-PORTAL`
   - Branch: `main`
   - Click: "Connect"

3. **Configure Service**:
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
   - **Region**: Same as database

4. **Add Environment Variables**:
   
   | Key | Value | Source |
   |-----|-------|--------|
   | `APP_ENV` | `production` | Static |
   | `DEBUG` | `false` | Static |
   | `SECRET_KEY` | Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"` | Static |
   | `DATABASE_URL` | From Step 2 (PostgreSQL Internal URL) | From Database |
   | `REDIS_URL` | `redis://localhost:6379/0` | Static |
   | `CORS_ORIGINS` | `https://ai-portal-frontend.onrender.com` | Static (will update after frontend URL) |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Static |
   | `DEMO_MODE` | `false` | Static |

5. **Create Service**:
   - Click: "Create Web Service"
   - Wait for build and deployment (~10-15 minutes)

6. **Monitor**:
   - Check: "Logs" tab for build progress
   - Wait for: "Service is live"
   - Copy: Your backend URL (e.g., `https://ai-portal-backend.onrender.com`)

---

## Step 4: Update Backend with Frontend URL

1. **After frontend deployment** (Step 5):
   - Go to backend service settings
   - Click: "Environment"
   - Edit: `CORS_ORIGINS`
   - Change: `https://ai-portal-frontend.onrender.com` (your actual frontend URL)
   - Save

2. **Service will auto-redeploy**

---

## Step 5: Deploy Frontend Service

1. **In Render Dashboard**:
   - Click: "New +" button
   - Select: "Web Service"

2. **Connect Repository**:
   - Select: "GitHub"
   - Repository: `AI-AUTOMATION-FOR-GOVERNMENT-PORTAL`
   - Branch: `main`
   - Click: "Connect"

3. **Configure Service**:
   - **Name**: `ai-portal-frontend`
   - **Environment**: Node
   - **Node Version**: 18.20.3 (or latest 18.x)
   - **Build Command**:
     ```bash
     cd frontend && npm install && npm run build
     ```
   - **Start Command**:
     ```bash
     cd frontend && npm run preview -- --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: Free
   - **Region**: Same as backend

4. **Environment Variables**:
   
   | Key | Value |
   |-----|-------|
   | `VITE_API_BASE_URL` | `https://ai-portal-backend.onrender.com/api/v1` |
   | `VITE_APP_NAME` | `AI Portal Automation` |

5. **Create Service**:
   - Click: "Create Web Service"
   - Wait for build and deployment (~10-15 minutes)

6. **Monitor**:
   - Check: "Logs" tab
   - Wait for: "Service is live"
   - Copy: Your frontend URL (e.g., `https://ai-portal-frontend.onrender.com`)

---

## Step 6: Final Configuration

1. **Update Backend CORS** (if not already done in Step 4):
   - Backend service → Environment
   - `CORS_ORIGINS`: `https://ai-portal-frontend.onrender.com`
   - Save

2. **Verify All Services Running**:
   - Dashboard view should show all 3 services with "Running" status
   - No "Build failed" or error messages

---

## Deployment URLs

After all services are running:

```
Frontend:    https://ai-portal-frontend.onrender.com
Backend:     https://ai-portal-backend.onrender.com
API Docs:    https://ai-portal-backend.onrender.com/docs
Health:      https://ai-portal-backend.onrender.com/api/v1/health
```

---

## Test Credentials

```
Email:    demo@ai-portal-demo.local
Password: DemoPassword@2026
```

---

## Verification Steps

### 1. Frontend Loading
- Visit: `https://ai-portal-frontend.onrender.com`
- Should see: Login page without errors

### 2. Login
- Email: `demo@ai-portal-demo.local`
- Password: `DemoPassword@2026`
- Should: Redirect to dashboard

### 3. Dashboard
- Should display: Metrics, activity, quick actions
- Should load without errors

### 4. API Health
- Visit: `https://ai-portal-backend.onrender.com/api/v1/health`
- Should see: `{"status":"healthy"}`

### 5. API Docs
- Visit: `https://ai-portal-backend.onrender.com/docs`
- Should see: Swagger UI with all endpoints

### 6. No Errors
- Open browser DevTools (F12)
- Check: Console tab
- Should see: No red errors

---

## Troubleshooting

### Build Failed

**Check logs**:
1. Service → Logs tab
2. Look for error message
3. Common issues:
   - Missing dependency in requirements.txt → Add to backend/requirements.txt
   - Wrong build command → Check Step 3 or 5
   - Environment variable missing → Check env vars

**Fix**:
1. Fix the code/config locally
2. Commit: `git commit -am "Fix deployment issue"`
3. Push: `git push`
4. Render will auto-redeploy

### Frontend Can't Connect to API

**Check**:
1. Verify `VITE_API_BASE_URL` is correct
2. Verify `CORS_ORIGINS` in backend includes frontend URL
3. Backend service is running

**Fix**:
1. Update environment variables
2. Restart services

### Database Connection Failed

**Check**:
1. `DATABASE_URL` is correct
2. Database service is running
3. Connection string format is correct

**Fix**:
1. Re-copy DATABASE_URL from database service
2. Update backend environment variable
3. Restart backend

---

## Important Notes

- **Free Tier**: Services spin down after 15 minutes of inactivity
- **First Request**: Takes ~5 seconds after spin-down
- **Storage**: 256MB database included
- **Build Time**: 5-15 minutes per service

---

## Next Steps After Deployment

1. ✅ Test all features
2. ✅ Monitor logs
3. ✅ Share with team
4. ⏳ (Optional) Upgrade to paid tier ($29+/month) for always-on services

---

## Support

- Render Docs: https://render.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- React Docs: https://react.dev

---

**Your code is ready.** Follow these steps in Render dashboard to deploy.

Good luck! 🚀
