# Testing Guide - New Features

## Quick Test Scenarios

### Test 1: Email Confirmation Flow
**What to test:** Email shows content before sending

**Steps:**
1. Say or type: "Send a follow-up email to HR about the onboarding documents"
2. Verify EmailForm modal opens
3. Check all fields are populated:
   - To: hr@company.com (or similar)
   - Subject: "Onboarding documents" or similar
   - Body: LLM-generated professional email
4. Edit if needed
5. Click "Send Email"
6. Verify success message

**Expected result:** Email form shows with full content, user can review/edit before sending

---

### Test 2: Voice + Typing Integration
**What to test:** Voice and typing work together

**Steps:**
1. Type in input field: "Send email to"
2. Click microphone button
3. Say: "john@example.com about the meeting"
4. Verify input field shows: "Send email to john@example.com about the meeting"

**Expected result:** Both inputs combined seamlessly with space between

---

### Test 3: Natural Language Task Creation
**What to test:** Task with "tomorrow" sets due date

**Steps:**
1. Say: "Create a task tomorrow to call the client"
2. Verify approval dialog shows:
   - Task title: "call the client"
   - Due: Tomorrow
3. Approve
4. Verify success message

**Alternative test:**
1. Say: "Remind me to submit the project tomorrow"
2. Verify task created with due date

**Expected result:** Due date automatically extracted and set

---

### Test 4: Tasks Manager UI
**What to test:** Full task management via UI

**Steps:**
1. Click "Tasks" button in top navigation
2. Verify TasksManager modal opens
3. Click "+ New Task"
4. Fill in:
   - Title: "Review quarterly report"
   - Notes: "Check all numbers"
   - Due Date: Select tomorrow
5. Click "Create Task"
6. Verify task appears in list with due date
7. Click "Done" button
8. Verify task marked as complete with checkmark
9. Click "Delete" button
10. Confirm deletion
11. Verify task removed

**Expected result:** All CRUD operations work via UI

---

### Test 5: Instant Meeting with Meet Link
**What to test:** Create meeting right now

**Steps:**
1. Say: "Create a meeting right now"
2. Verify approval dialog shows meeting details
3. Approve
4. Verify success message includes Google Meet link
5. Check Meet link format: https://meet.google.com/xxx-yyyy-zzz

**Expected result:** Meeting created instantly with Meet link displayed prominently

---

### Test 6: Scheduled Meeting with Attendees
**What to test:** Schedule meeting with natural language

**Steps:**
1. Say: "Schedule a team meeting tomorrow at 2 PM"
2. Verify approval dialog shows:
   - Title: "Team meeting"
   - Time: Tomorrow at 2 PM
3. Approve
4. Verify success message with Meet link

**Advanced test:**
1. Say: "Schedule design review tomorrow at 3 PM with alice@company.com and bob@company.com"
2. Verify approval shows attendees
3. Approve
4. Verify Meet link displayed

**Expected result:** Meeting scheduled with correct time and Meet link

---

### Test 7: List Upcoming Meetings
**What to test:** Retrieve meetings with Meet links

**Steps:**
1. Say: "Show my upcoming meetings"
2. Verify response lists events with:
   - Event title
   - Date/time
   - Meet link for each event
3. Format should be:
   ```
   📅 Event Name
      ⏰ Date/Time
      🔗 Meet Link
   ```

**Expected result:** All upcoming meetings listed with Meet links

---

### Test 8: Get Meet Link for Specific Event
**What to test:** Retrieve Meet link from existing event

**Steps:**
1. Say: "What is the Meet link for my next meeting?"
2. Verify response shows:
   - Meeting name
   - Meet link
3. Alternative: "Get the link for the team meeting"
4. Verify correct Meet link retrieved

**Expected result:** Meet link retrieved and displayed clearly

---

### Test 9: Natural Language Variations
**What to test:** Different phrasings work

**Email variations:**
- "Send mail to john@company.com"
- "Email HR about onboarding"
- "Send a message to support@company.com"

**Task variations:**
- "Add a task to review the document"
- "Remind me to call back tomorrow"
- "Create todo: finish the report"

**Meeting variations:**
- "Start a meeting now"
- "Schedule sync tomorrow at 10 AM"
- "Create meeting about project planning"

**Expected result:** All variations understood and handled correctly

---

### Test 10: Combined Voice and Text Workflow
**What to test:** Complete workflow using both input methods

**Steps:**
1. Type: "Schedule"
2. Speak: "a team meeting tomorrow at 2 PM"
3. Verify combined command works
4. Approve meeting
5. Click "Tasks" button
6. Create task via UI
7. Type: "Show my"
8. Speak: "upcoming meetings"
9. Verify meetings displayed with Meet links

**Expected result:** Seamless switching between voice, typing, and UI

---

## Edge Cases to Test

### Email Without Explicit Recipient:
- Say: "Send email to HR"
- Verify system creates placeholder: hr@company.com
- User can edit in EmailForm

### Task Without Clear Title:
- Say: "Create a task"
- Verify system uses full command as title
- Can still be edited via UI

### Meeting Without Time:
- Say: "Schedule a meeting"
- Verify system uses default time (current time or next hour)
- User can see time in approval dialog

---

## Regression Tests

Ensure existing features still work:

1. **Drive Search:**
   - Say: "Search Drive for attendance sheet"
   - Verify files listed with links

2. **Create Document:**
   - Say: "Create a document called Project Plan"
   - Verify approval and creation

3. **List Contacts:**
   - Say: "List my contacts"
   - Verify contacts displayed

4. **Create Note:**
   - Say: "Create a note about today's meeting"
   - Verify note created

---

## Performance Tests

1. **UI Responsiveness:**
   - Click Tasks button - should open instantly
   - Switch between task lists - should load quickly
   - Create task - should reflect immediately

2. **Voice Recognition:**
   - Speak clearly - should transcribe accurately
   - Click mic again - should stop recording

3. **Build Size:**
   - Frontend bundle: ~296 KB (acceptable)
   - Page load: Should be fast

---

## Common Issues and Solutions

### Issue: EmailForm doesn't show
**Solution:** Check browser console for errors. Ensure EMAIL_FORM response type returned.

### Issue: Voice transcription inaccurate
**Solution:** Speak clearly and check browser microphone permissions.

### Issue: TasksManager doesn't open
**Solution:** Check console for errors. Verify axios can reach backend.

### Issue: Meet link not showing
**Solution:** Verify Google Calendar API has conferenceData enabled. Check event response includes hangoutLink.

### Issue: Due date not parsing
**Solution:** Use "tomorrow" or "today" keywords. Specific dates coming in future update.

---

## Success Criteria

All features are working if:

- [ ] Email form shows before sending (with full content)
- [ ] Voice and typing combine without conflicts
- [ ] Natural language commands work (no rigid syntax needed)
- [ ] Tasks UI shows with all CRUD operations
- [ ] Instant meetings create with Meet links
- [ ] Scheduled meetings show Meet links
- [ ] Upcoming meetings can be listed with links
- [ ] Meet links can be retrieved for specific events
- [ ] Frontend builds without errors
- [ ] No console errors during operation

---

## Ready for Deployment

If all tests pass:
1. Commit all changes
2. Push to repository
3. Deploy backend to Render
4. Deploy frontend to Render
5. Verify production works same as local

**Your Vocal Agent is production-ready with all requested features!**
