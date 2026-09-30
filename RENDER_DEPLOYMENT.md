# Render Deployment Guide

This guide provides step-by-step instructions to deploy the AI Portal Automation Platform on Render.

---

## Prerequisites

- GitHub repository with the code pushed: https://github.com/durveshparab12345-cpu/AI-AUTOMATION-FOR-GOVERNMENT-PORTAL.git
- Render account: https://render.com (free tier available)
- PostgreSQL database (Render provides free tier)

---

## Deployment Steps

### Step 1: Connect GitHub to Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Select **"Connect a repository"**
4. Authorize GitHub and select: `durveshparab12345-cpu/AI-AUTOMATION-FOR-GOVERNMENT-PORTAL`
5. Click **"Connect"**

### Step 2: Deploy Backend Service

1. **Service Name**: `ai-portal-backend`
2. **Environment**: Python 3.10
3. **Build Command**:
   ```bash
   cd backend && pip install -r requirements.txt && python -m alembic upgrade head
   ```
4. **Start Command**:
   ```bash
   cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
5. **Instance Type**: Free
6. **Environment Variables**:

   | Key | Value |
   |-----|-------|
   | `APP_ENV` | `production` |
   | `DEBUG` | `false` |
   | `SECRET_KEY` | *(Generate secure key)* |
   | `DATABASE_URL` | *(Render will provide)* |
   | `CORS_ORIGINS` | `https://YOUR_FRONTEND_URL.onrender.com` |
   | `DEMO_MODE` | `false` |

7. Click **"Create Web Service"**
8. Wait for build to complete (5-10 minutes)
9. Copy the backend URL (e.g., `https://ai-portal-backend.onrender.com`)

### Step 3: Add PostgreSQL Database

1. In Render dashboard, click **"New +"** → **"PostgreSQL"**
2. **Name**: `ai-portal-db`
3. **Database**: `ai_portal_prod`
4. **User**: `postgres`
5. **Instance Type**: Free
6. Click **"Create Database"**
7. Copy the connection string (provided on the database details page)

### Step 4: Update Backend with Database Connection

1. Go back to backend service settings
2. Add environment variable:
   - **Key**: `DATABASE_URL`
   - **Value**: *(Paste PostgreSQL connection string from Step 3)*
3. Click **"Save"**
4. Trigger a new deploy

### Step 5: Deploy Frontend Service

1. Create new **Web Service**
2. **Service Name**: `ai-portal-frontend`
3. **Environment**: Node 18
4. **Build Command**:
   ```bash
   cd frontend && npm install && npm run build
   ```
5. **Start Command**:
   ```bash
   cd frontend && npm run preview -- --host 0.0.0.0
   ```
6. **Instance Type**: Free
7. **Environment Variables**:

   | Key | Value |
   |-----|-------|
   | `VITE_API_BASE_URL` | `https://ai-portal-backend.onrender.com/api/v1` |
   | `VITE_APP_NAME` | `AI Portal Automation` |

8. Click **"Create Web Service"**
9. Wait for build to complete
10. Copy the frontend URL (e.g., `https://ai-portal-frontend.onrender.com`)

### Step 6: Update Backend CORS

1. Go to backend service → **Environment**
2. Update `CORS_ORIGINS` to: `https://ai-portal-frontend.onrender.com`
3. Click **"Save"**
4. Trigger new deploy

### Step 7: Test the Deployment

1. Open frontend URL: `https://ai-portal-frontend.onrender.com`
2. Login with demo credentials:
   - Email: `demo@ai-portal-demo.local`
   - Password: `DemoPassword@2026`
3. Verify API endpoints at: `https://ai-portal-backend.onrender.com/docs`

---

## Database Initialization

The database is automatically initialized when the backend service starts (via Alembic migrations).

To manually initialize:
1. Go to backend service → **Shell**
2. Run:
   ```bash
   cd backend
   python -m alembic upgrade head
   ```

---

## Monitoring & Logs

### View Logs
1. Select service in Render dashboard
2. Click **"Logs"** tab
3. Watch real-time deployment and runtime logs

### Health Checks
- Backend: `https://ai-portal-backend.onrender.com/api/v1/health`
- Frontend: Visit home page and check for 200 status

### Troubleshooting

**Backend build fails**:
- Check logs for missing dependencies
- Verify `backend/requirements.txt` is correct
- Ensure Python version is 3.10+

**Frontend build fails**:
- Check Node version (18+)
- Verify `frontend/package.json` exists
- Check `npm run build` works locally first

**Database connection error**:
- Verify `DATABASE_URL` is set correctly
- Check database instance is running
- Run migrations manually if needed

**CORS errors**:
- Update `CORS_ORIGINS` in backend environment
- Restart backend service
- Clear browser cache

---

## Environment Variables Reference

### Backend (.env or Render Environment)
```
APP_NAME=AI Portal Automation Platform
APP_ENV=production
DEBUG=false
SECRET_KEY=<generate-strong-key>
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=https://your-frontend-url.onrender.com
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DEMO_MODE=false
```

### Frontend (.env.local or Render Environment)
```
VITE_API_BASE_URL=https://your-backend-url.onrender.com/api/v1
VITE_APP_NAME=AI Portal Automation
VITE_APP_VERSION=0.2.0
```

---

## Scaling Considerations

### Free Tier Limitations
- Services spin down after 15 minutes of inactivity
- Database: 256MB storage limit
- Limited to 1 concurrent request per service
- No custom domains

### Upgrading to Paid Plans
1. Go to service settings
2. Click **"Plan"** → Select plan
3. Upgrade includes:
   - Always-on services
   - More storage
   - Better performance
   - Custom domains
   - SSL certificates

---

## Updating Deployment

### Deploy Code Changes
1. Push changes to GitHub:
   ```bash
   git add .
   git commit -m "Update feature"
   git push origin main
   ```
2. Render automatically redeploys on push
3. Monitor deployment in Render dashboard

### Update Dependencies
1. Update `requirements.txt` or `package.json`
2. Commit and push
3. Render rebuilds with new dependencies

### Database Migrations
1. Create new migration locally:
   ```bash
   cd backend
   alembic revision --autogenerate -m "Add new table"
   ```
2. Commit and push
3. New deploy automatically runs migrations

---

## Backup & Recovery

### Database Backup
- Render provides automatic backups for paid plans
- For free tier, manually export data:
  ```bash
  pg_dump <connection-string> > backup.sql
  ```

### Restore from Backup
```bash
psql <connection-string> < backup.sql
```

---

## Cost Estimation (Monthly)

| Service | Free Tier | Paid Tier |
|---------|-----------|-----------|
| Backend | $0 | $7+ |
| Frontend | $0 | $7+ |
| Database | $0 | $7+ |
| **Total** | **$0** | **$21+** |

---

## Next Steps

1. ✅ Push code to GitHub
2. ✅ Deploy backend on Render
3. ✅ Deploy PostgreSQL on Render
4. ✅ Deploy frontend on Render
5. ✅ Test all features
6. ✅ Configure custom domain (paid plan)
7. ✅ Set up CI/CD for auto-deployment
8. ✅ Monitor performance and logs

---

## Support & Resources

- **Render Docs**: https://render.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **React Docs**: https://react.dev
- **PostgreSQL Docs**: https://www.postgresql.org/docs

---

## Render URLs After Deployment

- **Backend API**: `https://ai-portal-backend.onrender.com`
- **Backend API Docs**: `https://ai-portal-backend.onrender.com/docs`
- **Frontend**: `https://ai-portal-frontend.onrender.com`

Replace with your actual service names if different.

