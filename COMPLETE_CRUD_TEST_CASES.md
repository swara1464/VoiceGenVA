# Complete CRUD Functionality Test Cases
## Vocal Agent - Google Workspace Integration

This document provides complete test cases for all CRUD operations across all Google APIs.

---

## 📧 Gmail API - COMPLETE ✅

### ✅ CREATE - Send Email
**Test Command:**
```
Send email to test@example.com saying "Hello World" subject "Test Email"
```

**Expected Result:**
- Email preview modal appears with all fields
- User can edit/approve/cancel
- On approval, email is sent via Gmail API
- Email appears in sent folder

**Alternative Test:**
```
Send email to john@example.com cc jane@example.com bcc boss@example.com saying "Meeting notes attached" subject "Project Update"
```

### ✅ READ - Search & Read Emails
**Test Command 1 - Search:**
```
Search my inbox for emails from john
```

**Expected Result:**
- Returns list of emails from john@*
- Shows sender, subject, date, snippet

**Test Command 2 - List Unread:**
```
Show me unread emails
```

**Expected Result:**
- Returns list of unread emails
- Maximum 10 results by default

**Test Command 3 - Read Specific:**
```
Read email with ID [message_id]
```

**Expected Result:**
- Returns full email content
- Shows headers, body, attachments

### ✅ UPDATE - Modify Email Labels
**Test Command 1 - Mark as Read:**
```
Mark email [message_id] as read
```

**Expected Result:**
- Email removed from UNREAD label
- Confirmation message returned

**Test Command 2 - Archive:**
```
Archive email [message_id]
```

**Expected Result:**
- Email removed from INBOX
- Still accessible via All Mail

**Test Command 3 - Star:**
```
Star email [message_id]
```

**Expected Result:**
- Email marked with star
- Appears in Starred folder

### ✅ DELETE - Trash Email
**Test Command:**
```
Delete email [message_id]
```

**Expected Result:**
- Email moved to Trash
- Recoverable for 30 days

---

## 📅 Calendar API - COMPLETE ✅

### ✅ CREATE - Schedule Event
**Test Command:**
```
Schedule a team meeting tomorrow at 10 AM
```

**Expected Result:**
- Event created in Google Calendar
- IST timezone applied
- Returns event link

### ✅ READ - List Events
**Test Command:**
```
Show me my upcoming events
```

**Expected Result:**
- Lists next 10 upcoming events
- Shows title, time, attendees

### ✅ UPDATE - Modify Event
**Test Command:**
```
Reschedule "Team Meeting" to 2 PM tomorrow
```

**Expected Result:**
- Finds event by title
- Updates start/end time
- Sends notifications to attendees

### ✅ DELETE - Cancel Event
**Test Command:**
```
Cancel the event titled "Team Sync"
```

**Expected Result:**
- Event deleted from calendar
- Attendees notified of cancellation

---

## ✅ Tasks API - COMPLETE ✅

### ✅ CREATE - Add Task
**Test Command:**
```
Create task "Finish Project Report"
```

**Expected Result:**
- Task added to default task list
- Shows in Google Tasks

### ✅ READ - List Tasks
**Test Command:**
```
Show me my tasks
```

**Expected Result:**
- Lists all tasks with status
- Shows title, notes, due date

### ✅ UPDATE - Modify Task
**Test Command:**
```
Update task [task_id] with new title "Complete Final Report"
```

**Expected Result:**
- Task title updated
- Notes/due date can also be updated

**Alternative (Mark Complete):**
```
Mark task "Finish Report" as complete
```

**Expected Result:**
- Task status changed to completed
- Checked off in Google Tasks

### ✅ DELETE - Remove Task
**Test Command:**
```
Delete task [task_id]
```

**Expected Result:**
- Task permanently deleted
- No longer appears in task list

---

## 👥 Contacts API - COMPLETE ✅

### ✅ CREATE - Add Contact
**Test Command:**
```
Add contact John Doe with email john@example.com and phone +1234567890
```

**Expected Result:**
- New contact created in Google Contacts
- All fields saved correctly

### ✅ READ - Search Contacts
**Test Command:**
```
What is John's phone number?
```

**Expected Result:**
- Searches contacts for "John"
- Returns name, email, phone

### ✅ UPDATE - Modify Contact
**Test Command:**
```
Update contact [resource_name] with new email newemail@example.com
```

**Expected Result:**
- Contact email updated
- Changes sync across Google services

### ✅ DELETE - Remove Contact
**Test Command:**
```
Delete contact [resource_name]
```

**Expected Result:**
- Contact permanently deleted
- Removed from all Google services

---

## 💾 Drive API - COMPLETE ✅

### ✅ CREATE - Upload File
**Test Command:**
```
Upload file "notes.txt" with content "Meeting notes from today"
```

**Expected Result:**
- File created in Google Drive
- Returns file ID and link

### ✅ READ - Search Files
**Test Command:**
```
Search my drive for "Project Report"
```

**Expected Result:**
- Returns list of matching files
- Shows name, ID, link, modified date

### ✅ UPDATE - Rename File
**Test Command:**
```
Rename file [file_id] to "Final Project Report"
```

**Expected Result:**
- File renamed in Drive
- Link remains the same

### ✅ DELETE - Remove File
**Test Command:**
```
Delete file [file_id] from drive
```

**Expected Result:**
- File moved to Trash
- Recoverable for 30 days

---

## 📄 Docs API - COMPLETE ✅

### ✅ CREATE - New Document
**Test Command:**
```
Create a new document called "2026 Ideas"
```

**Expected Result:**
- New Google Doc created
- Returns doc ID and link
- Opens in Google Docs

### ✅ READ - View Document
**Test Command:**
```
Read document [doc_id]
```

**Expected Result:**
- Returns full document content
- Shows title and text

### ✅ UPDATE - Edit Document
**Test Command 1 - Append:**
```
Add text "These are my ideas for 2026" to document [doc_id]
```

**Expected Result:**
- Text appended to end of document
- Preserves existing content

**Test Command 2 - Replace:**
```
Replace "ideas" with "plans" in document [doc_id]
```

**Expected Result:**
- All occurrences of "ideas" changed to "plans"
- Returns number of replacements made

### ✅ DELETE - Remove Document
**Test Command:**
```
Delete document [doc_id]
```

**Expected Result:**
- Document moved to Trash
- Recoverable for 30 days

---

## 📊 Sheets API - COMPLETE ✅

### ✅ CREATE - New Spreadsheet
**Test Command:**
```
Create a new spreadsheet called "Budget 2026"
```

**Expected Result:**
- New Google Sheet created
- Returns sheet ID and link

### ✅ READ - View Data
**Test Command:**
```
Read data from Sheet1!A1:B5 in spreadsheet [sheet_id]
```

**Expected Result:**
- Returns cell values as 2D array
- Shows all data in range

### ✅ UPDATE - Modify Cells
**Test Command 1 - Update Cell:**
```
Update cell A1 to "Total Budget" in spreadsheet [sheet_id]
```

**Expected Result:**
- Cell A1 updated with new value
- Changes saved immediately

**Test Command 2 - Add Row:**
```
Add row ["Item", "100", "USD"] to spreadsheet [sheet_id]
```

**Expected Result:**
- New row appended to sheet
- Values placed in columns A, B, C

### ✅ DELETE - Remove Spreadsheet
**Test Command:**
```
Delete spreadsheet [sheet_id]
```

**Expected Result:**
- Spreadsheet moved to Trash
- Recoverable for 30 days

---

## 📊 CRUD Completeness Summary

| API Service | Create | Read | Update | Delete | Complete? |
|------------|--------|------|--------|--------|-----------|
| **Gmail** | ✅ Send | ✅ Search/Read | ✅ Labels | ✅ Trash | **YES** ✅ |
| **Calendar** | ✅ Event | ✅ List | ✅ Modify | ✅ Cancel | **YES** ✅ |
| **Tasks** | ✅ Add | ✅ List | ✅ Edit/Complete | ✅ Delete | **YES** ✅ |
| **Contacts** | ✅ Add | ✅ Search | ✅ Edit | ✅ Delete | **YES** ✅ |
| **Drive** | ✅ Upload | ✅ Search | ✅ Rename | ✅ Delete | **YES** ✅ |
| **Docs** | ✅ Create | ✅ Read | ✅ Append/Replace | ✅ Delete | **YES** ✅ |
| **Sheets** | ✅ Create | ✅ Read | ✅ Update/AddRow | ✅ Delete | **YES** ✅ |

---

## 🧪 How to Test Each Operation

### Prerequisites:
1. ✅ Backend deployed at `vocalagentapi.onrender.com`
2. ✅ Frontend deployed at `voicegenva.onrender.com`
3. ✅ User authenticated with Google OAuth
4. ✅ All required scopes granted

### Testing Process:

#### For CREATE operations:
1. Enter voice command or type in chat
2. Verify LLM correctly identifies action
3. Confirm resource is created in Google service
4. Check success message and returned IDs/links

#### For READ operations:
1. Enter search/list command
2. Verify results match Google service data
3. Check formatting and completeness

#### For UPDATE operations:
1. Get resource ID from CREATE or READ operation
2. Enter update command with ID
3. Verify changes in Google service
4. Confirm success message

#### For DELETE operations:
1. Get resource ID from CREATE or READ operation
2. Enter delete command with ID
3. Verify resource moved to trash (or deleted)
4. Confirm deletion message

---

## 🎯 Accuracy Metrics to Measure

For your professor's evaluation, track:

1. **Intent Recognition Accuracy**
   - % of commands correctly identified as CRUD operation
   - Target: >95%

2. **Execution Success Rate**
   - % of API calls that succeed
   - Target: >95%

3. **Parameter Extraction Accuracy**
   - % of commands where all parameters extracted correctly
   - Target: >90%

4. **End-to-End Success Rate**
   - % of commands that complete fully from voice → Google API
   - Target: >85%

5. **Response Time**
   - Average time from command → result
   - Target: <5 seconds

---

## 📝 Sample Test Script

```bash
# Gmail CRUD
✅ "Send email to test@example.com saying 'Test' subject 'Test'"
✅ "Show me unread emails"
✅ "Mark email [id] as read"
✅ "Delete email [id]"

# Calendar CRUD
✅ "Schedule meeting tomorrow at 2 PM"
✅ "Show my upcoming events"
✅ "Reschedule 'Team Sync' to 3 PM"
✅ "Cancel event 'Daily Standup'"

# Tasks CRUD
✅ "Create task 'Buy groceries'"
✅ "Show me my tasks"
✅ "Mark 'Buy groceries' as complete"
✅ "Delete task [id]"

# Contacts CRUD
✅ "Add contact John with email john@test.com"
✅ "What is John's email?"
✅ "Update contact [id] with phone +1234567890"
✅ "Delete contact [id]"

# Drive CRUD
✅ "Upload file test.txt"
✅ "Search drive for 'report'"
✅ "Rename file [id] to 'final-report.txt'"
✅ "Delete file [id]"

# Docs CRUD
✅ "Create document 'Notes'"
✅ "Read document [id]"
✅ "Add 'Hello World' to document [id]"
✅ "Delete document [id]"

# Sheets CRUD
✅ "Create spreadsheet 'Budget'"
✅ "Read Sheet1!A1:B2 from [id]"
✅ "Update cell A1 to 'Total' in [id]"
✅ "Delete spreadsheet [id]"
```

---

## ✅ ALL CRUD OPERATIONS COMPLETE

**Status: READY FOR PROFESSOR DEMO** 🎓

All 28 CRUD operations across 7 Google APIs are fully implemented and tested.
