# Complete Deployment Checklist

**Project**: AI Portal Automation Platform  
**Repository**: https://github.com/durveshparab12345-cpu/AI-AUTOMATION-FOR-GOVERNMENT-PORTAL.git  
**Deployment Target**: Render  
**Status**: Ready for Deployment

---

## Pre-Deployment Checklist

- [ ] Code is on main branch
- [ ] All files committed to Git
- [ ] No uncommitted changes
- [ ] `.gitignore` file present
- [ ] Environment files (.env) are in .gitignore
- [ ] No secrets in committed code
- [ ] `requirements.txt` is complete
- [ ] `package.json` is complete
- [ ] Database migrations are included
- [ ] Docker files are present
- [ ] Documentation is complete

**Status**: ✅ All Ready

```bash
# Verify with:
cd "c:\Users\hp\Desktop\AI AUTOMATION FOR PMJAY"
git status  # Should show: "On branch main, nothing to commit"
```

---

## Deployment Sequence

### Step 1: GitHub Setup (5 min)

#### 1.1 Create Personal Access Token
- [ ] Go to https://github.com/settings/tokens
- [ ] Click "Generate new token" → "Classic"
- [ ] Name: `AI-Portal-Automation`
- [ ] Select `repo` + `workflow` scopes
- [ ] Click "Generate token"
- [ ] **Copy token** (save it safely)

#### 1.2 Push Code to GitHub
```bash
cd "c:\Users\hp\Desktop\AI AUTOMATION FOR PMJAY"

# Configure Git credentials
git config --global credential.helper manager-core

# Push code
git push -u origin main

# When prompted:
# Username: durveshparab12345
# Password: <paste your token>
```

- [ ] Code successfully pushed
- [ ] Verify on https://github.com/durveshparab12345-cpu/AI-AUTOMATION-FOR-GOVERNMENT-PORTAL
- [ ] Recent commit is visible

---

### Step 2: Render Account Setup (2 min)

- [ ] Go to https://render.com
- [ ] Click "Sign Up"
- [ ] Choose "Continue with GitHub"
- [ ] Authorize Render to access GitHub
- [ ] Complete profile
- [ ] Verify email

**Render Dashboard**: https://dashboard.render.com

---

### Step 3: Deploy Backend (15 min)

#### 3.1 Create Web Service
- [ ] Dashboard → **"New"** → **"Web Service"**
- [ ] Select repository: `AI-AUTOMATION-FOR-GOVERNMENT-PORTAL`
- [ ] Click "Connect"

#### 3.2 Configure Backend Service
| Setting | Value |
|---------|-------|
| Name | `ai-portal-backend` |
| Environment | Python 3.10 |
| Region | (Any) |
| Branch | `main` |
| Build Command | `cd backend && pip install -r requirements.txt && python -m alembic upgrade head` |
| Start Command | `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Plan | Free |

- [ ] Build command entered
- [ ] Start command entered
- [ ] Free plan selected

#### 3.3 Add Environment Variables
| Key | Value |
|-----|-------|
| `APP_ENV` | `production` |
| `DEBUG` | `false` |
| `SECRET_KEY` | Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `CORS_ORIGINS` | `*` (will update after frontend deployment) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` |
| `DEMO_MODE` | `false` |

- [ ] All environment variables added
- [ ] SECRET_KEY is strong (32+ chars)

#### 3.4 Create Service
- [ ] Click "Create Web Service"
- [ ] Monitor build logs (5-10 minutes)
- [ ] Build completes successfully
- [ ] Service shows "Running"
- [ ] Copy service URL: `https://ai-portal-backend.onrender.com` (example)

**Backend URL**: `https://ai-portal-backend.onrender.com`

---

### Step 4: Deploy PostgreSQL Database (5 min)

#### 4.1 Create Database
- [ ] Dashboard → **"New"** → **"PostgreSQL"**

#### 4.2 Configure Database
| Setting | Value |
|---------|-------|
| Name | `ai-portal-db` |
| Database | `ai_portal_prod` |
| User | `postgres` |
| Plan | Free |
| Region | (Same as backend) |

- [ ] All settings configured
- [ ] Free plan selected

#### 4.3 Create Database
- [ ] Click "Create Database"
- [ ] Wait for database to be ready (2-3 minutes)
- [ ] Database shows "Available"
- [ ] Copy **Internal Database URL**

**Important**: Use **INTERNAL** URL, not public URL

---

### Step 5: Connect Database to Backend (5 min)

#### 5.1 Update Backend Environment
- [ ] Go to backend service
- [ ] Settings → **Environment**
- [ ] Add new variable:
  - **Key**: `DATABASE_URL`
  - **Value**: <paste internal URL from Step 4>

#### 5.2 Verify Format
- Database URL should look like:
  ```
  postgresql+asyncpg://postgres:password@host:5432/ai_portal_prod
  ```

#### 5.3 Save and Redeploy
- [ ] Click "Save"
- [ ] Redeploy backend service
- [ ] Check logs: "Application startup complete"
- [ ] Health check: `https://ai-portal-backend.onrender.com/api/v1/health`
  - Expected: `{"status": "healthy"}`

---

### Step 6: Deploy Frontend (15 min)

#### 6.1 Create Web Service
- [ ] Dashboard → **"New"** → **"Web Service"**
- [ ] Select repository: `AI-AUTOMATION-FOR-GOVERNMENT-PORTAL`

#### 6.2 Configure Frontend Service
| Setting | Value |
|---------|-------|
| Name | `ai-portal-frontend` |
| Environment | Node 18 |
| Region | (Same as backend) |
| Branch | `main` |
| Build Command | `cd frontend && npm install && npm run build` |
| Start Command | `cd frontend && npm run preview -- --host 0.0.0.0` |
| Plan | Free |

- [ ] All settings configured

#### 6.3 Add Environment Variables
| Key | Value |
|-----|-------|
| `VITE_API_BASE_URL` | `https://ai-portal-backend.onrender.com/api/v1` |
| `VITE_APP_NAME` | `AI Portal Automation` |

- [ ] Backend URL is correct
- [ ] Use full backend URL (from Step 3)

#### 6.4 Create Service
- [ ] Click "Create Web Service"
- [ ] Monitor build logs
- [ ] Build completes successfully
- [ ] Service shows "Running"
- [ ] Copy service URL: `https://ai-portal-frontend.onrender.com` (example)

**Frontend URL**: `https://ai-portal-frontend.onrender.com`

---

### Step 7: Final Integration (5 min)

#### 7.1 Update Backend CORS
- [ ] Go to backend service → Environment
- [ ] Update `CORS_ORIGINS`:
  ```
  https://ai-portal-frontend.onrender.com
  ```
- [ ] Click Save → Redeploy

#### 7.2 Verify Integration
- [ ] Open frontend URL in browser
- [ ] Page loads successfully
- [ ] No 502/503 errors
- [ ] No CORS errors in console

---

## Post-Deployment Verification

### Test 1: Health Check
```bash
curl https://ai-portal-backend.onrender.com/api/v1/health
```

Expected Response:
```json
{"status": "healthy"}
```

- [ ] Returns 200 OK
- [ ] Status is "healthy"

### Test 2: API Documentation
- [ ] Open: https://ai-portal-backend.onrender.com/docs
- [ ] Swagger UI loads
- [ ] All endpoints visible
- [ ] Try expanding endpoints

### Test 3: Frontend Login
- [ ] Open: https://ai-portal-frontend.onrender.com
- [ ] Page loads without errors
- [ ] Login form visible
- [ ] Email field shows: `demo@ai-portal-demo.local`

### Test 4: Login Functionality
- [ ] Email: `demo@ai-portal-demo.local`
- [ ] Password: `DemoPassword@2026`
- [ ] Click "Sign in"
- [ ] Dashboard loads successfully
- [ ] Metrics cards visible
- [ ] Recent activity feed shows

### Test 5: Navigation
- [ ] Click "Portals" in sidebar → Portal page loads
- [ ] Click "Workflows" → Workflows page loads
- [ ] Click "Cases" → Cases page loads
- [ ] Click "Automations" → Automations page loads

### Test 6: API Functionality
- [ ] Open browser DevTools (F12)
- [ ] Check Network tab
- [ ] Make an action (e.g., navigate between pages)
- [ ] Verify API calls in Network tab
- [ ] All requests show 200 status

### Test 7: Error Handling
- [ ] Open API docs: `/docs`
- [ ] Try invalid endpoint: `/invalid-endpoint`
- [ ] Should return 404
- [ ] Try without auth header: Make API call
- [ ] Should return 401 Unauthorized

---

## Deployment Summary

| Service | URL | Status |
|---------|-----|--------|
| Backend | `https://ai-portal-backend.onrender.com` | ✅ |
| Frontend | `https://ai-portal-frontend.onrender.com` | ✅ |
| Database | PostgreSQL via Render | ✅ |
| Repository | https://github.com/durveshparab12345-cpu/AI-AUTOMATION-FOR-GOVERNMENT-PORTAL.git | ✅ |

---

## Credentials Reference

### Demo User
```
Email:    demo@ai-portal-demo.local
Password: DemoPassword@2026
```

### Database
```
Database: ai_portal_prod
User:     postgres
Password: (Set during creation)
Host:     (Provided by Render)
```

### GitHub
```
Username: durveshparab12345
Repo:     AI-AUTOMATION-FOR-GOVERNMENT-PORTAL
Token:    (Generated for deployment)
```

---

## Important URLs

### Live Application
- **Frontend**: https://ai-portal-frontend.onrender.com
- **Backend**: https://ai-portal-backend.onrender.com
- **API Docs**: https://ai-portal-backend.onrender.com/docs
- **Health**: https://ai-portal-backend.onrender.com/api/v1/health

### Management
- **Render Dashboard**: https://dashboard.render.com
- **GitHub Repository**: https://github.com/durveshparab12345-cpu/AI-AUTOMATION-FOR-GOVERNMENT-PORTAL
- **GitHub Settings**: https://github.com/settings/tokens

### Documentation
- **Local Project**: `c:\Users\hp\Desktop\AI AUTOMATION FOR PMJAY`
- **Deployment Guide**: `RENDER_DEPLOYMENT.md`
- **GitHub Instructions**: `GITHUB_PUSH_INSTRUCTIONS.md`
- **Quick Start**: `QUICKSTART.md`

---

## Troubleshooting Guide

| Issue | Solution |
|-------|----------|
| Build fails | Check build logs, verify dependencies |
| Database error | Use Internal URL, check connection string format |
| CORS error | Update CORS_ORIGINS, restart backend |
| Login fails | Check SECRET_KEY, verify demo user exists |
| API 502 error | Check backend logs, verify start command |
| Frontend blank page | Check console for errors, verify API_BASE_URL |

---

## Next Steps (Optional)

After successful deployment:

1. **Custom Domain** (Paid plan)
   - Configure custom domain
   - Set up SSL certificate
   - Update CORS_ORIGINS

2. **Monitoring**
   - Set up error tracking
   - Configure alerts
   - Monitor performance

3. **CI/CD**
   - Automatic tests on push
   - Auto-deploy on merge
   - Staging environment

4. **Scaling** (Paid plan)
   - Upgrade to standard tier
   - Enable auto-scaling
   - Add caching layer

---

## Final Checklist

**Pre-Deployment**:
- [x] Code committed
- [x] All dependencies included
- [x] Configuration files present
- [x] Documentation complete

**Deployment**:
- [ ] GitHub Personal Access Token created
- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Backend deployed
- [ ] PostgreSQL deployed
- [ ] Frontend deployed
- [ ] Services connected

**Post-Deployment**:
- [ ] Health check passes
- [ ] Frontend loads
- [ ] Login works
- [ ] API calls succeed
- [ ] All pages accessible

**Documentation**:
- [x] Deployment guide written
- [x] GitHub instructions provided
- [x] Troubleshooting guide included
- [x] URLs documented

---

## Success Confirmation

When all items are checked:

✅ **Application is LIVE on Render**  
✅ **Ready for production use**  
✅ **Auto-deployed on code push**  
✅ **Database persists data**  
✅ **Users can access and use the platform**  

---

**Deployment Status**: 🎉 **Ready to Launch**

Follow the checklist above to deploy successfully!

