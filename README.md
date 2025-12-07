# VoiceGenVA

**Status:** FULLY FUNCTIONAL AND DEMO-READY  

VoiceGenVA is a voice-controlled AI assistant for Google Workspace, designed to automate productivity tasks using natural language. It leverages modern LLM-driven architecture to provide a seamless, secure, and hands-free experience.

## I. Key Features and Supported Services

VoiceGenVA integrates across eight core Google Workspace services, enabling voice (STT) input and real-time feedback (TTS).

### Core Features
- **LLM-Driven Planning:** Uses the Cohere LLM as the "brain" to convert natural language into structured JSON action plans.
- **Security & Approval Flow:** Sensitive actions (e.g., sending emails, creating documents, scheduling events) require user approval via an explicit modal.
- **Persistent Storage:** Execution logs and OAuth tokens are safely stored in a SQLite3 database with thread-safe locking.
- **Natural Language Support:** Handles complex queries, date parsing (e.g., "tomorrow at 2 PM"), and contact resolution.
- **Voice Integration:** Full Speech-to-Text input and Text-to-Speech output with toggle support.

### Supported Google Workspace Services
| Service   | Primary Actions                                 | Status      |
|----------|-------------------------------------------------|------------|
| Gmail     | Send Email, Search Inbox, List Unread, Read Email | ✅ High    |
| Calendar  | Create Event, Instant Meet, List/Update/Delete Event | ✅ High |
| Tasks     | Create, List, Complete, Delete Tasks           | ✅ High    |
| Docs      | Create Document, Append Content, Search (via Drive) | ⚠️ Partial |
| Sheets    | Create Spreadsheet, Add Row, Read Data         | ⚠️ Partial |
| Drive     | Search Files (owned and shared)                | ⚠️ Partial |
| Contacts  | Search, List, Create Contact                   | ✅ High    |
| Keep      | Create, List, Edit Note (via Docs workaround)  | ⚠️ Workaround |

## II. System Architecture

VoiceGenVA follows a modular architecture for maintainability and scalability.

### Architecture Flow
1. **User Input:** Voice (Web Speech API) or Text sent to Flask Backend.
2. **Planner (`backend/planner/router.py`):** Converts input into a JSON action plan using Cohere LLM.
3. **Executor (`backend/agent/executor.py`):** Dispatches JSON plan to relevant Google API wrapper (e.g., `gmail_utils.py`).
4. **API Execution:** Google API calls are made using the user's OAuth token.
5. **Logging:** Execution status (`ATTEMPTING`, `SUCCESS`, `FAILED`) recorded in `logs.db`.
6. **Response:** Result or approval request sent back to the frontend.

### Project Structure & Key Endpoints
| Component  | Directory                       | Function                                 | Key Endpoints                                      |
|-----------|---------------------------------|-----------------------------------------|---------------------------------------------------|
| Backend    | `backend/`                      | Flask server, Core Logic, API Wrappers  | POST `/planner/run`, POST `/agent/execute`, GET `/logs` |
| Frontend   | `frontend/`                     | React UI, Voice Input, Chat Interface   | GET `/`, GET `/agent`, GET `/dashboard`          |
| Planner    | `backend/planner/`              | Converts natural language to JSON plan (Cohere LLM) | -                                                 |
| Executor   | `backend/agent/`                | Dispatches actions to Google APIs       | -                                                 |
| Services   | `backend/google_services/`      | Wrappers for all 8 Google APIs          | -                                                 |
| Persistence| `backend/models/session_store.py`| Supabase token and log persistence          | -                                                 |

## III. Setup and Installation

### Prerequisites
- Python 3.10+
- Node.js 16+
- Google Cloud project with OAuth credentials
- Cohere API key

### Local Development Setup

# Clone repository
git clone [repository_url]
cd VoiceGenVA-f06cffc5ca184178749845825fedf2ada767fb70

### Backend Setup
cd backend
pip install -r requirements.txt

Create a `.env` file inside `backend/`:

COHERE_API_KEY=your_cohere_api_key_here
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
SESSION_SECRET=your_random_session_secret_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabse_service_key_here

### Configure Google OAuth
Add this Authorized Redirect URI in Google Cloud Console:
http://localhost:5050/auth/callback

Add your email to `ALLOWED_TESTERS` in `backend/auth/google_oauth.py`.

### Run Backend
python app.py
# Backend runs at: http://localhost:5050

### Frontend Setup
cd ../frontend
npm install
npm run dev
# Frontend runs at: http://localhost:5173

## IV. Deployment and Testing

### Deployment Guide (Render Monorepo)
- Update URLs in `frontend/src/axios.js` and `backend/auth/google_oauth.py` with your Render URLs.
- Add environment variables (`COHERE_API_KEY`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `SESSION_SECRET`,`SUPABASE_URL`,`SUPABASE_KEY`) to Render Backend Service.

### Backend Command (Gunicorn)
gunicorn --bind 0.0.0.0:$PORT app:app

### Frontend
Static site build — SPA routing enabled (rewrite `/.*` → `/index.html`)

### Security Note
After deployment, log out and re-authenticate to grant all required OAuth scopes.

### Essential Demo Commands
| Feature | Command | Expected Result |
|--------|---------|----------------|
| Email | Send email to [YOUR_EMAIL] subject "Demo Test" saying "This is a test email" | EMAIL_PREVIEW modal opens → Click Send → Email arrives |
| Calendar | Schedule a team meeting tomorrow at 9 AM | APPROVAL modal opens → Approve → Event created with Meet link |
| Instant Meet | Create an instant meeting right now | Instant event created → Meet link displayed |
| Tasks | Create a task to complete the quarterly report | APPROVAL modal opens → Approve → Task created |
| Drive Search | Search my drive for Devops Report | List of matching files with clickable links |
| Contacts | What is Swara's email? | Contact name, email, phone displayed |
| Small Talk | hi how are you | Natural conversational response |

## V. Notes & Limitations

- Docs, Sheets, Drive, and Keep integrations are partially supported or use workarounds.
- Approval Modals are required for sensitive actions.
- Designed for personal productivity automation — not mass emailing or bulk operations.
