# backend/google_services/calendar_utils.py
from .gmail_utils import get_google_service # Reuse the auth function

def create_calendar_event(summary: str, description: str, start_time: str, end_time: str, attendees: list = None):
    """
    Creates a new calendar event with Google Meet conferencing.
    
    :param summary: Event title.
    :param description: Event description.
    :param start_time: Start datetime (e.g., '2025-12-03T09:00:00-07:00').
    :param end_time: End datetime.
    :param attendees: List of attendee emails.
    """
    service, error = get_google_service("calendar", "v3")
    if error:
        return {"success": False, "message": error}

    event = {
        'summary': summary,
        'description': description,
        'start': {'dateTime': start_time, 'timeZone': 'America/Los_Angeles'}, # Placeholder TZ
        'end': {'dateTime': end_time, 'timeZone': 'America/Los_Angeles'},     # Placeholder TZ
        'conferenceData': {
            'createRequest': {
                'requestId': 'agent-meet-request',
                'conferenceSolutionKey': {'type': 'hangoutsMeet'},
            },
        },
        'attendees': [{'email': email} for email in attendees] if attendees else [],
        'reminders': {'useDefault': True},
    }

    try:
        # 'primary' is a special ID for the user's main calendar
        event = service.events().insert(
            calendarId='primary', 
            body=event, 
            conferenceDataVersion=1
        ).execute()
        
        meet_link = event.get('hangoutLink')
        
        return {
            "success": True,
            "message": f"Calendar event '{summary}' created successfully.",
            "details": {
                "event_id": event.get('id'),
                "meet_link": meet_link
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to create calendar event: {e}"}