# Render Deployment Guide - Complete Setup

## Overview
Your Vocal Agent application is now fully configured for production deployment on Render. This guide provides step-by-step instructions to deploy both the frontend and backend.

## Architecture
- **Frontend**: `https://voicegenva.onrender.com` (Static site with React Router)
- **Backend**: `https://vocalagentapi.onrender.com` (Flask API with Google OAuth)
- **Database**: Supabase PostgreSQL (persistent, never expires)

---

## Part 1: Database Setup (Supabase)

### Status: ✅ COMPLETE
A `logs` table has been created in Supabase with the following structure:
- `id` (uuid, primary key)
- `timestamp` (automatic, when action was executed)
- `user_email` (user who triggered action)
- `action` (action type: GMAIL_SEND, CALENDAR_CREATE, etc.)
- `status` (ATTEMPTING, SUCCESS, FAILED)
- `details` (JSON data with execution results)

**RLS Security**: Users can only view their own logs. Logs are append-only (cannot be modified/deleted).

---

## Part 2: Environment Variables Setup

### For Backend Deployment (vocalagentapi.onrender.com)

Add these environment variables in Render Dashboard → Settings → Environment Variables:

```
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>
SESSION_SECRET=vocal_agent_session_secret_key_2024
SUPABASE_URL=https://pgvvjyqsczsffdaoarkl.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBndnZqeXFzY3pzZmZkYW9hcmtsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDk5MTMzMSwiZXhwIjoyMDgwNTY3MzMxfQ.LnE5g-QoFYaT0pQm5K2VdJfH1WM8_xNbXRQ_pYT0_-Q
```

**Google OAuth Credentials**:
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create OAuth 2.0 credentials (Web Application)
3. Add authorized redirect URIs:
   - `https://vocalagentapi.onrender.com/auth/callback`
4. Copy Client ID and Secret to environment variables

### For Frontend Deployment (voicegenva.onrender.com)

No environment variables needed. Frontend automatically uses:
- Supabase URL and Anon Key from build-time config
- Backend URL: `https://vocalagentapi.onrender.com`

---

## Part 3: Backend Deployment

### Configuration Files Updated
- ✅ `backend/render.yaml` - Complete Render configuration
- ✅ `backend/requirements.txt` - Added supabase and gunicorn
- ✅ `backend/logs/log_utils.py` - Uses Supabase instead of SQLite
- ✅ `backend/app.py` - Updated for Supabase logs

### Deploy to Render

1. **Create new Web Service**:
   - Name: `vocal-agent-backend`
   - Runtime: Python 3.10
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT app:app`
   - Instance Type: Free or Paid

2. **Connect GitHub**:
   - Link your repository
   - Set branch: `main` (or your working branch)

3. **Set Environment Variables**:
   - Add all variables from Part 2
   - Ensure FLASK_ENV is set to "production"

4. **Deploy**:
   - Click "Create Web Service"
   - Render will automatically build and deploy

### Verify Backend Health
```
curl https://vocalagentapi.onrender.com/health
# Should return: {"status": "ok"}
```

---

## Part 4: Frontend Deployment

### Configuration Files Updated
- ✅ `frontend/render.yaml` - Complete service definition with build config
- ✅ `frontend/src/axios.js` - Points to backend at `https://vocalagentapi.onrender.com`

### Deploy to Render

1. **Create new Static Site**:
   - Name: `voicegenva-frontend`
   - Build Command: `npm install && npm run build`
   - Publish Directory: `dist`
   - Environment: Static

2. **Connect GitHub**:
   - Same repository
   - Set branch: `main` (or your working branch)

3. **Deploy**:
   - Click "Create Static Site"
   - Render will build and serve from `dist` folder

### Verify Frontend
- Visit `https://voicegenva.onrender.com`
- You should see the login page
- SPA routing (/dashboard, /agent, /history) should work

---

## Part 5: OAuth Configuration

### Google Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select your project
3. Go to APIs & Services → Credentials
4. Find or create OAuth 2.0 credentials (Web Application type)
5. Under "Authorized redirect URIs", add:
   ```
   https://vocalagentapi.onrender.com/auth/callback
   ```
6. Copy the Client ID and Secret to your backend environment variables

### Test OAuth Flow

1. Visit `https://voicegenva.onrender.com`
2. Click "Login with Google"
3. You should be redirected to Google
4. After approval, redirected back to `https://voicegenva.onrender.com/dashboard?login=success`
5. Dashboard should load with your logs history

---

## Part 6: Verify Full Functionality

### Login & Authentication
- [ ] Can login with Google (must be in ALLOWED_TESTERS)
- [ ] Session persists across page refreshes
- [ ] Logout works correctly

### API Endpoints
- [ ] `/health` returns 200 OK
- [ ] `/auth/me` returns user info when logged in
- [ ] `/logs` returns execution history
- [ ] `/agent/execute` accepts action requests (requires login)

### Frontend Routing
- [ ] `/` (login page) loads
- [ ] `/dashboard` loads after login
- [ ] `/agent` loads after login
- [ ] `/history` loads after login
- [ ] Direct navigation (refresh) to routes still works (SPA routing fix)

### Database Persistence
- [ ] Execute an agent action
- [ ] Check `/logs` endpoint - should show the action
- [ ] Refresh page - log should still be there
- [ ] Logs persist across deployments

---

## Part 7: Troubleshooting

### Issue: "Cannot GET /dashboard" or similar routes return 404

**Solution**: Frontend render.yaml must include SPA routing rules:
```yaml
routes:
  - type: rewrite
    source: /.*
    destination: /index.html
```

**Status**: ✅ Already configured in `frontend/render.yaml`

### Issue: Login redirects to wrong URL or session not persisting

**Solution**: Verify CORS configuration in backend:
- Origins must include `https://voicegenva.onrender.com`
- `supports_credentials=True` must be set
- Session cookies must use `SameSite=None` and `Secure=True`

**Status**: ✅ Already configured in `backend/app.py`

### Issue: Google login fails with "Redirect URI mismatch"

**Solution**: Ensure Google Console has correct redirect URI:
```
https://vocalagentapi.onrender.com/auth/callback
```

**Status**: ✅ Already configured in `backend/auth/google_oauth.py`

### Issue: Logs not persisting between deployments

**Solution**: Must use Supabase instead of SQLite (ephemeral)

**Status**: ✅ Already implemented - logs now use Supabase

### Issue: "GOOGLE_CLIENT_ID not found" or similar env var errors

**Solution**: Set all environment variables in Render Dashboard:
- Backend service needs: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, SESSION_SECRET, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

**Status**: ✅ Guide provided in Part 2

---

## Summary of Changes Made

### Database Migration
- Migrated from SQLite (`executions.db`) to Supabase PostgreSQL
- Created `logs` table with RLS policies
- Updated `backend/logs/log_utils.py` to use Supabase client

### Frontend Configuration
- Fixed `frontend/render.yaml` with complete service definition
- Added SPA routing rewrite rules
- Verified `axios.js` points to correct backend

### Backend Configuration
- Created `backend/render.yaml` with production settings
- Added `gunicorn` to requirements.txt
- Updated `app.py` to disable debug mode in production
- Updated CORS to allow frontend domain
- Updated session configuration for cross-domain cookies

### Environment Setup
- Updated `.env` with Supabase credentials
- Added placeholders for Google OAuth credentials
- Added SESSION_SECRET

---

## Quick Deployment Checklist

Before deploying, ensure:
- [ ] GitHub repository is up to date with all changes
- [ ] Both frontend and backend have render.yaml files
- [ ] Backend environment variables are ready in Render dashboard
- [ ] Google OAuth credentials are configured
- [ ] Supabase database is accessible (logs table created)

---

## Next Steps

1. **Commit & Push**: Push all changes to your GitHub repository
   ```bash
   git add .
   git commit -m "Complete production deployment configuration"
   git push origin main
   ```

2. **Deploy Backend First**:
   - Create web service on Render pointing to backend directory
   - Set environment variables
   - Deploy

3. **Deploy Frontend Second**:
   - Create static site on Render pointing to frontend directory
   - Deploy

4. **Test Complete Flow**:
   - Visit frontend URL
   - Login with Google
   - Execute an action
   - Verify logs persist

5. **Monitor**:
   - Check Render logs for any errors
   - Monitor database usage on Supabase
   - Track API response times

---

## Support

For issues:
1. Check Render deployment logs
2. Verify all environment variables are set
3. Test backend health endpoint
4. Check browser console for frontend errors
5. Verify Supabase connection and RLS policies

---

**Status**: ✅ Application is fully configured and ready for production deployment
