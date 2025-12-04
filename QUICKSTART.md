# Vocal Agent - Quick Start Guide

## Prerequisites

### Required:
- Python 3.10+
- Node.js 16+
- Google Cloud Console project with OAuth configured
- Cohere API key

---

## Setup Instructions

### 1. Backend Setup

#### Install Dependencies:
```bash
cd backend
pip install -r requirements.txt
```

#### Configure Environment Variables:
Create a `.env` file in the `backend` directory:

```env
# Cohere API
COHERE_API_KEY=your_cohere_api_key_here

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Session Security
SESSION_SECRET=your_random_session_secret_here
```

#### Update Allowed Testers:
Edit `backend/auth/google_oauth.py`:
```python
ALLOWED_TESTERS = ["your.email@gmail.com", "tester2@gmail.com"]
```

#### Run Backend:
```bash
cd backend
python app.py
```

Backend will run on `http://localhost:5050`

---

### 2. Frontend Setup

#### Install Dependencies:
```bash
cd frontend
npm install
```

#### Run Frontend:
```bash
npm run dev
```

Frontend will run on `http://localhost:5173`

---

## Google Cloud Console Configuration

### 1. Create OAuth 2.0 Credentials
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Navigate to: APIs & Services → Credentials
- Create OAuth 2.0 Client ID
- Application type: Web application

### 2. Configure OAuth Consent Screen
Add all required scopes:
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

### 3. Add Authorized Redirect URIs
```
http://localhost:5050/auth/callback
```

### 4. Add Test Users
Add all tester email addresses to the OAuth consent screen

---

## Testing the Application

### 1. Access the Application
Open browser to: `http://localhost:5173`

### 2. Login
- Click "Login with Google"
- Select your Google account (must be in ALLOWED_TESTERS list)
- Grant all requested permissions

### 3. Navigate to Voice Agent
After login, click "Open Voice Agent" from the dashboard

### 4. Try Voice Commands

#### Using Microphone:
1. Click the green "Speak" button
2. Say your command (e.g., "Create a task to review documents")
3. Command appears in input field
4. Click "Send" or press Enter

#### Using Text:
1. Type command in the input field
2. Press Enter or click "Send"

### 5. Test Different Services

**Tasks:**
- "Create a task to finish the report"
- "List my tasks"

**Calendar:**
- "Schedule a meeting tomorrow at 2 PM"

**Drive:**
- "Search Drive for project files"

**Documents:**
- "Create a document called Meeting Notes"

**Sheets:**
- "Create a spreadsheet for budget tracking"

**Notes:**
- "Create a note about today's discussion"

**Contacts:**
- "Find contact for John"

### 6. View Execution History
- Click "History" button in top navigation
- View all executed actions with status indicators
- Click "View Details" to see full execution data

### 7. Voice Response Toggle
- Use the "Voice Response" checkbox to enable/disable TTS
- When enabled, the agent speaks all responses

---

## Common Commands to Test

### 1. Simple Single-Action Commands
```
"Search Drive for attendance"
"List my tasks"
"Show my contacts"
"Create a note about the meeting"
```

### 2. Commands Requiring Approval
```
"Send an email to hr@company.com"
"Schedule a meeting next Monday at 3 PM"
"Create a task to complete the budget"
"Create a document called Project Plan"
```

### 3. Search Commands (Execute Immediately)
```
"Search Drive for budget files"
"Find contacts named John"
"Show my notes"
"List my tasks"
```

---

## Approval Flow

For sensitive actions (email, calendar, creating documents), the system will:
1. Display an approval modal with action details
2. Wait for user to approve or reject
3. Execute only if approved
4. Speak the result

---

## Troubleshooting

### Backend Issues

**Port 5050 already in use:**
```bash
# Kill the process using port 5050
lsof -ti:5050 | xargs kill -9
```

**Missing dependencies:**
```bash
pip install -r requirements.txt --force-reinstall
```

**Import errors:**
```bash
cd backend
python app.py
```
Ensure you're running from the `backend` directory.

### Frontend Issues

**Port 5173 already in use:**
```bash
# Kill the process
lsof -ti:5173 | xargs kill -9
```

**Module not found:**
```bash
rm -rf node_modules package-lock.json
npm install
```

### Google OAuth Issues

**Redirect URI Mismatch:**
- Verify `http://localhost:5050/auth/callback` is in Google Console
- Check `REDIRECT_URI` in `google_oauth.py` matches exactly

**Unauthorized Email:**
- Add your email to `ALLOWED_TESTERS` in `google_oauth.py`
- Add as test user in Google Cloud Console

**Missing Scopes:**
- Logout and login again to grant new permissions
- Verify all scopes are added in Google Console

### LLM Issues

**Cohere API Error:**
- Verify `COHERE_API_KEY` is set correctly in `.env`
- Check API key is active at [cohere.com](https://cohere.com)

**Empty Responses:**
- Check backend console for error messages
- Verify `command-a-03-2025` model is available

---

## File Structure

```
vocal-agent/
├── backend/
│   ├── agent/
│   │   ├── executor.py         # Action dispatcher
│   │   └── __init__.py
│   ├── auth/
│   │   ├── google_oauth.py     # OAuth login/logout
│   │   └── __init__.py
│   ├── google_services/
│   │   ├── gmail_utils.py      # Gmail operations
│   │   ├── calendar_utils.py   # Calendar operations
│   │   ├── drive_utils.py      # Drive operations
│   │   ├── docs_utils.py       # Docs operations
│   │   ├── sheets_utils.py     # Sheets operations
│   │   ├── tasks_utils.py      # Tasks operations
│   │   ├── keep_utils.py       # Notes operations
│   │   ├── contacts_utils.py   # Contacts operations
│   │   └── __init__.py
│   ├── logs/
│   │   ├── log_utils.py        # Execution logging
│   │   └── __init__.py
│   ├── planner/
│   │   ├── router.py           # LLM planner
│   │   └── __init__.py
│   ├── app.py                  # Flask server
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── LoginPage.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── History.jsx
│   │   │   ├── MicButton.jsx
│   │   │   ├── ChatBubble.jsx
│   │   │   └── ApprovalModal.jsx
│   │   ├── App.jsx
│   │   ├── axios.js
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
├── IMPROVEMENTS.md
└── QUICKSTART.md
```

---

## API Endpoints

### Backend Routes:

**Authentication:**
- `GET /auth/login` - Initiate Google OAuth
- `GET /auth/callback` - OAuth callback
- `GET /auth/me` - Get current user
- `GET /auth/logout` - Logout

**Agent:**
- `POST /planner/run` - Send voice command for planning
- `POST /agent/execute` - Execute approved action
- `GET /logs` - Get execution history

**Health:**
- `GET /health` - Health check
- `GET /` - Root endpoint

---

## Environment Variables Reference

### Backend (.env)
```env
COHERE_API_KEY=<your_cohere_api_key>
GOOGLE_CLIENT_ID=<your_google_client_id>
GOOGLE_CLIENT_SECRET=<your_google_client_secret>
SESSION_SECRET=<random_string_for_session_encryption>
```

### Frontend
No environment variables needed for local development.
Backend URL is hardcoded in `src/axios.js` as `http://localhost:5050`

---

## Database

The system uses SQLite for execution logs:
- Database file: `backend/executions.db`
- Auto-created on first run
- Stores all action attempts and results
- User-specific logs

---

## Demo Tips

### For Best Results:
1. Use clear, specific commands
2. Wait for the "thinking" indicator before speaking again
3. Enable Voice Response for full demo effect
4. Show the History page to demonstrate logging
5. Demonstrate approval flow with email/calendar commands

### Impressive Demo Commands:
```
"Search Drive for project files"
"Create a task to complete the quarterly report"
"Schedule a team meeting next Friday at 2 PM"
"Find contact for Sarah"
"Create a document called Sprint Planning"
```

---

## Next Steps

1. Test all service integrations
2. Add more complex multi-step workflows
3. Improve date/time parsing in the planner
4. Add more detailed execution results
5. Deploy to production (Render + Vercel/Netlify)

---

## Support

For issues or questions:
- Check the backend console for error logs
- Check the browser console for frontend errors
- Review the execution history for failed actions
- Verify all OAuth scopes are granted

---

**Happy Testing!**
