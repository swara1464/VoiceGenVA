# Quick Start: Deploy to Render (5 Minutes)

## What Was Fixed

✅ Frontend SPA routing now works (no more 404 on `/dashboard`, `/agent`, `/history`)
✅ Backend CORS configured for production domains
✅ Database migrated from SQLite to persistent Supabase
✅ OAuth flow properly configured
✅ All build artifacts ready
✅ Production configuration complete

## Step 1: Add Google OAuth Credentials (2 min)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create/select a project
3. Go to **APIs & Services → Credentials**
4. Create "OAuth 2.0 Client ID" (Web Application type)
5. Under "Authorized redirect URIs", add:
   ```
   https://vocalagentapi.onrender.com/auth/callback
   ```
6. Copy **Client ID** and **Client Secret**

## Step 2: Push Code to GitHub (1 min)

```bash
cd /tmp/cc-agent/61155720/project
git add .
git commit -m "Production deployment: fix routing, migrate to Supabase, configure CORS"
git push origin main
```

## Step 3: Deploy Backend to Render (1 min)

1. Go to [Render.com](https://render.com)
2. Click **New →  Web Service**
3. Select your GitHub repository
4. Fill in:
   - **Name**: `vocal-agent-backend`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3.10
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`
   - **Instance Type**: Free or Paid

5. **Add Environment Variables**:
   ```
   GOOGLE_CLIENT_ID=<your-client-id>
   GOOGLE_CLIENT_SECRET=<your-client-secret>
   FLASK_ENV=production
   SESSION_SECRET=vocal_agent_session_secret_key_2024
   SUPABASE_URL=https://pgvvjyqsczsffdaoarkl.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBndnZqeXFzY3pzZmZkYW9hcmtsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDk5MTMzMSwiZXhwIjoyMDgwNTY3MzMxfQ.LnE5g-QoFYaT0pQm5K2VdJfH1WM8_xNbXRQ_pYT0_-Q
   ```

6. Click **Create Web Service**
7. Wait for deployment to complete (~3-5 min)
8. Note the URL: `https://vocal-agent-backend.onrender.com` (or your custom domain if configured as `vocalagentapi.onrender.com`)

## Step 4: Deploy Frontend to Render (1 min)

1. Go to [Render.com](https://render.com)
2. Click **New → Static Site**
3. Select your GitHub repository
4. Fill in:
   - **Name**: `voicegenva-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

5. Click **Create Static Site**
6. Wait for deployment to complete (~2-3 min)
7. Note the URL: `https://voicegenva.onrender.com`

## Step 5: Verify Everything Works (1 min)

### Test Backend Health
```bash
curl https://vocal-agent-backend.onrender.com/health
# Should return: {"status": "ok"}
```

### Test Frontend
1. Visit: `https://voicegenva.onrender.com`
2. You should see the login page
3. Click **Login with Google**
4. Authenticate with your Google account (must be in allowed testers)
5. You should be redirected to the dashboard
6. You should see your logs (empty at first)

### Test SPA Routing
1. Navigate to `/dashboard` → should work
2. Navigate to `/agent` → should work
3. Navigate to `/history` → should work
4. Refresh page → should NOT get 404 (SPA routing working)

### Test Logs Persistence
1. Execute an agent action
2. Check the history tab → action should appear
3. Logout and login again → action should still appear
4. Deploy again → action should still be there (Supabase persists)

## Done! 🎉

Your app is now fully deployed on Render with:
- ✅ No more 404 errors on routes
- ✅ Working OAuth login
- ✅ Persistent database
- ✅ Production-ready configuration
- ✅ Cross-domain CORS
- ✅ Secure session cookies

## If Something Goes Wrong

### Issue: "Redirect URI mismatch" on Google login

**Fix**: Go to Google Cloud Console → Credentials → OAuth 2.0 Client → Add:
```
https://vocal-agent-backend.onrender.com/auth/callback
```
(Replace with your actual backend URL)

### Issue: "Cannot GET /dashboard" after login

**Fix**: Frontend render.yaml must have SPA routing. Check it includes:
```yaml
routes:
  - type: rewrite
    source: /.*
    destination: /index.html
```

### Issue: Login works but session not persisting

**Fix**: Backend CORS must include your frontend domain. Verify:
```python
CORS(
    app,
    origins=["https://voicegenva.onrender.com", "http://localhost:5173"],
    supports_credentials=True,
)
```

### Issue: No logs showing up

**Fix**: Ensure backend environment variables are set in Render dashboard:
- SUPABASE_URL
- SUPABASE_SERVICE_ROLE_KEY

## Documentation

- **Full Guide**: See `RENDER_DEPLOYMENT_GUIDE.md`
- **Validation Report**: See `DEPLOYMENT_VALIDATION.md`
- **Changes Made**: See commit history

---

**Status**: Your app is production-ready and should be fully functional after these steps!
