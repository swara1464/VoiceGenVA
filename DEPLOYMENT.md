# Vocal Agent - Production Deployment Guide

## Overview
This guide covers deploying your Vocal Agent system to production using:
- **Backend:** Render
- **Frontend:** Vercel or Netlify

---

## Pre-Deployment Checklist

- [ ] Google Cloud Console OAuth configured for production URLs
- [ ] Cohere API key ready
- [ ] Production domain/URLs decided
- [ ] Tester email list finalized
- [ ] Session secret generated

---

## Part 1: Backend Deployment (Render)

### Step 1: Prepare Backend for Deployment

#### 1.1 Create Render Configuration
The `backend/render.yaml` file should contain:

```yaml
services:
  - type: web
    name: vocal-agent-backend
    env: python
    region: oregon
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
    envVars:
      - key: COHERE_API_KEY
        sync: false
      - key: GOOGLE_CLIENT_ID
        sync: false
      - key: GOOGLE_CLIENT_SECRET
        sync: false
      - key: SESSION_SECRET
        generateValue: true
      - key: PORT
        value: 5050
```

#### 1.2 Update Google OAuth Redirect URI

In `backend/auth/google_oauth.py`, you'll need to update after getting your Render URL:

```python
# Change from:
REDIRECT_URI = "http://localhost:5050/auth/callback"

# To (after deployment):
REDIRECT_URI = "https://your-app-name.onrender.com/auth/callback"
```

### Step 2: Deploy to Render

#### 2.1 Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub

#### 2.2 Connect Repository
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Select the `vocal-agent` repository

#### 2.3 Configure Service
- **Name:** `vocal-agent-backend`
- **Region:** Oregon (or closest to your users)
- **Branch:** `main`
- **Root Directory:** `backend`
- **Runtime:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python app.py`

#### 2.4 Set Environment Variables
In Render dashboard, add:

```
COHERE_API_KEY=<your_cohere_api_key>
GOOGLE_CLIENT_ID=<your_google_client_id>
GOOGLE_CLIENT_SECRET=<your_google_client_secret>
SESSION_SECRET=<generate_random_string_here>
PORT=5050
```

**Generate SESSION_SECRET:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

#### 2.5 Deploy
1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Note your service URL: `https://your-app-name.onrender.com`

### Step 3: Update Production Settings

#### 3.1 Update `google_oauth.py`
After deployment, update the redirect URI:

```python
# Production
REDIRECT_URI = "https://your-app-name.onrender.com/auth/callback"

# Also update the frontend redirect after login
return redirect("https://your-frontend-url.vercel.app/dashboard?login=success")
```

#### 3.2 Update CORS Settings
In `backend/app.py`, update CORS origins:

```python
CORS(
    app,
    origins=["https://your-frontend-url.vercel.app"],  # Update this
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"]
)

# Also update in after_request:
@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "https://your-frontend-url.vercel.app")
    # ... rest of headers
```

#### 3.3 Redeploy
Commit changes and push to trigger auto-deploy on Render.

---

## Part 2: Frontend Deployment (Vercel)

### Step 1: Prepare Frontend

#### 1.1 Update Backend URL
In `frontend/src/axios.js`:

```javascript
import axios from "axios";

axios.defaults.withCredentials = true;
axios.defaults.baseURL = "https://your-app-name.onrender.com";  // Update this

export default axios;
```

#### 1.2 Update OAuth Redirect
In `frontend/src/components/LoginPage.jsx`:

```javascript
const handleLogin = () => {
  window.open("https://your-app-name.onrender.com/auth/login", "_self");
};
```

### Step 2: Deploy to Vercel

#### 2.1 Install Vercel CLI (Optional)
```bash
npm install -g vercel
```

#### 2.2 Deploy via CLI
```bash
cd frontend
vercel
```

Follow prompts:
- Project name: `vocal-agent`
- Directory: `./`
- Override settings? No

#### 2.3 Deploy via Dashboard (Alternative)

1. Go to [vercel.com](https://vercel.com)
2. Import your Git repository
3. Configure:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`

4. Click "Deploy"

#### 2.4 Note Your URL
After deployment: `https://vocal-agent.vercel.app` (or custom domain)

---

## Part 3: Google Cloud Console Production Setup

### Step 1: Update OAuth Configuration

#### 1.1 Authorized Redirect URIs
Add production callback:
```
https://your-app-name.onrender.com/auth/callback
```

Keep localhost for development:
```
http://localhost:5050/auth/callback
```

#### 1.2 Authorized JavaScript Origins
Add both:
```
https://your-frontend-url.vercel.app
http://localhost:5173
```

### Step 2: OAuth Consent Screen

#### 2.1 Publishing Status
- For testing: Keep as "Testing" and add test users
- For public: Submit for verification (requires domain verification)

#### 2.2 Verify All Scopes
Ensure all required scopes are added:
- openid
- email
- profile
- https://www.googleapis.com/auth/gmail.send
- https://www.googleapis.com/auth/calendar.events
- https://www.googleapis.com/auth/drive
- https://www.googleapis.com/auth/documents
- https://www.googleapis.com/auth/spreadsheets
- https://www.googleapis.com/auth/tasks
- https://www.googleapis.com/auth/contacts.readonly

#### 2.3 Add Production Test Users
Add all authorized tester emails in Google Console.

---

## Part 4: Final Backend Updates

### Update All Production URLs

After both deployments, update `backend/auth/google_oauth.py`:

```python
# Production URLs
REDIRECT_URI = "https://vocal-agent-backend.onrender.com/auth/callback"

# In callback function:
return redirect("https://vocal-agent.vercel.app/dashboard?login=success")
```

### Update CORS in `backend/app.py`:

```python
CORS(
    app,
    origins=["https://vocal-agent.vercel.app"],
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"]
)

@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "https://vocal-agent.vercel.app")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    return response
```

### Commit and Push
```bash
git add .
git commit -m "Update production URLs"
git push
```

Render will auto-deploy the changes.

---

## Part 5: Testing Production Deployment

### 1. Test Backend Health
```bash
curl https://your-app-name.onrender.com/health
```
Expected: `{"status": "ok"}`

### 2. Test Frontend
Visit: `https://vocal-agent.vercel.app`

### 3. Test Full Flow
1. Click "Login with Google"
2. Authorize all scopes
3. Navigate to Voice Agent
4. Try a command: "Search Drive for files"
5. Check execution history

### 4. Test All Services
Run test commands for each service:
- Gmail
- Calendar
- Drive
- Docs
- Sheets
- Tasks
- Notes
- Contacts

---

## Environment Variables Summary

### Render (Backend)
```
COHERE_API_KEY=<your_key>
GOOGLE_CLIENT_ID=<your_id>
GOOGLE_CLIENT_SECRET=<your_secret>
SESSION_SECRET=<random_64_char_hex>
PORT=5050
```

### Vercel (Frontend)
No environment variables needed. All configuration is in code.

---

## Security Considerations

### 1. Session Security
- Use a strong, random SESSION_SECRET (64+ characters)
- Never commit secrets to Git
- Use environment variables for all sensitive data

### 2. CORS Configuration
- Only allow your production frontend domain
- Don't use wildcard "*" in production
- Maintain `withCredentials: true` for session cookies

### 3. OAuth Security
- Keep `GOOGLE_CLIENT_SECRET` secure
- Only add trusted test users
- Monitor OAuth usage in Google Console

### 4. API Keys
- Protect your Cohere API key
- Monitor API usage for anomalies
- Set up billing alerts

---

## Monitoring and Logging

### Render Monitoring
- View logs: Render Dashboard → Logs
- Monitor resource usage
- Set up health check alerts

### Error Tracking
- Check Render logs for backend errors
- Check browser console for frontend errors
- Review execution history in the app

### Performance
- Monitor Render response times
- Check Vercel analytics
- Optimize slow endpoints

---

## Troubleshooting Production Issues

### CORS Errors
**Symptom:** "CORS policy blocked" in browser console

**Fix:**
1. Verify frontend URL in `app.py` CORS config
2. Check `after_request` headers
3. Ensure `withCredentials: true` in axios config

### OAuth Redirect Mismatch
**Symptom:** "redirect_uri_mismatch" error

**Fix:**
1. Check REDIRECT_URI in `google_oauth.py`
2. Verify exact match in Google Console
3. Include/exclude trailing slash consistently

### Session Cookie Issues
**Symptom:** User logged out after page refresh

**Fix:**
1. Ensure `SESSION_COOKIE_SECURE=True` for HTTPS
2. Set `SESSION_COOKIE_SAMESITE="None"` for cross-origin
3. Verify `withCredentials: true` in all axios requests

### Database Not Persisting
**Symptom:** Execution history lost after redeploy

**Fix:**
Render's filesystem is ephemeral. For production:
1. Use Render Postgres for persistent storage
2. Or use external database (e.g., Supabase)
3. Update `log_utils.py` to use production database

---

## Custom Domain Setup (Optional)

### For Frontend (Vercel)
1. Go to Vercel Dashboard → Project Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed
4. Update CORS settings in backend

### For Backend (Render)
1. Go to Render Dashboard → Settings → Custom Domain
2. Add your custom domain
3. Update DNS records
4. Update OAuth redirect URIs
5. Update frontend axios baseURL

---

## Scaling Considerations

### Backend (Render)
- **Free tier:** 512 MB RAM, sleeps after inactivity
- **Paid tiers:** Always-on, more resources
- Consider upgrading for production use

### Database
- Current: SQLite (ephemeral on Render)
- Production: Migrate to Render Postgres or external DB

### API Rate Limits
- Monitor Cohere API usage
- Monitor Google API quotas
- Implement rate limiting if needed

---

## Backup and Recovery

### Code
- Push all code to GitHub
- Use branches for production/development
- Tag releases

### Database
If using persistent storage:
- Regular automated backups
- Test restore procedures
- Store backups off-site

### Environment Variables
- Document all variables
- Store securely (password manager)
- Never commit to Git

---

## Deployment Checklist

- [ ] Backend deployed to Render
- [ ] Frontend deployed to Vercel
- [ ] Environment variables set
- [ ] OAuth redirect URIs updated
- [ ] CORS configuration updated
- [ ] Session settings configured
- [ ] All URLs updated in code
- [ ] Test users added in Google Console
- [ ] Full end-to-end testing completed
- [ ] Error logging verified
- [ ] Performance tested
- [ ] Documentation updated

---

## Maintenance

### Regular Tasks
- Monitor error logs weekly
- Review API usage monthly
- Update dependencies quarterly
- Renew OAuth verification annually (if public)

### Updates
- Test updates in development first
- Use Git branches for new features
- Deploy during low-traffic periods
- Monitor after deployment

---

## Support URLs

- **Render Status:** https://status.render.com
- **Vercel Status:** https://status.vercel.com
- **Google Cloud Status:** https://status.cloud.google.com
- **Cohere Status:** https://status.cohere.com

---

## Production URLs (Template)

After deployment, document your URLs:

```
Frontend: https://vocal-agent.vercel.app
Backend: https://vocal-agent-backend.onrender.com
OAuth Callback: https://vocal-agent-backend.onrender.com/auth/callback
Google Console: https://console.cloud.google.com/apis/credentials?project=<your-project>
```

---

**Your Vocal Agent is now live!**

Test thoroughly, monitor logs, and enjoy your production AI agent system.
