# backend/google_services/calendar_utils.py
from .gmail_utils import get_google_service # Reuse the auth function

def create_calendar_event(summary: str, description: str, start_time: str, end_time: str, attendees: list = None, user_email: str = None):
    """
    Creates a new calendar event with Google Meet conferencing.

    :param summary: Event title.
    :param description: Event description.
    :param start_time: Start datetime (e.g., '2025-12-03T09:00:00-07:00').
    :param end_time: End datetime.
    :param attendees: List of attendee emails.
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("calendar", "v3", user_email)
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


def get_upcoming_events(max_results: int = 10, user_email: str = None):
    """
    Retrieves upcoming calendar events with their Meet links.

    :param max_results: Maximum number of events to return.
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("calendar", "v3", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        import datetime
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        if not events:
            return {"success": False, "message": "No upcoming events found."}

        event_list = []
        for event in events:
            event_data = {
                'id': event.get('id'),
                'summary': event.get('summary', 'No Title'),
                'start': event.get('start', {}).get('dateTime', event.get('start', {}).get('date')),
                'end': event.get('end', {}).get('dateTime', event.get('end', {}).get('date')),
                'meet_link': event.get('hangoutLink', 'No Meet link'),
                'description': event.get('description', ''),
                'attendees': [attendee.get('email') for attendee in event.get('attendees', [])]
            }
            event_list.append(event_data)

        return {
            "success": True,
            "message": f"Found {len(event_list)} upcoming events.",
            "details": event_list
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to retrieve upcoming events: {e}"}


def get_event_meet_link(event_id: str = None, summary_search: str = None, user_email: str = None):
    """
    Retrieves the Meet link for a specific event.
    Can search by event ID or event title.

    :param event_id: Specific event ID to retrieve.
    :param summary_search: Search term to find event by title.
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("calendar", "v3", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        if event_id:
            # Get specific event by ID
            event = service.events().get(calendarId='primary', eventId=event_id).execute()
            meet_link = event.get('hangoutLink', 'No Meet link available')
            return {
                "success": True,
                "message": f"Meet link for '{event.get('summary')}': {meet_link}",
                "details": {
                    'summary': event.get('summary'),
                    'meet_link': meet_link,
                    'start': event.get('start', {}).get('dateTime', event.get('start', {}).get('date'))
                }
            }

        elif summary_search:
            # Search for event by title
            import datetime
            now = datetime.datetime.utcnow().isoformat() + 'Z'

            events_result = service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy='startTime',
                q=summary_search
            ).execute()

            events = events_result.get('items', [])

            if not events:
                return {"success": False, "message": f"No upcoming events found matching '{summary_search}'."}

            # Return first matching event
            event = events[0]
            meet_link = event.get('hangoutLink', 'No Meet link available')

            return {
                "success": True,
                "message": f"Meet link for '{event.get('summary')}': {meet_link}",
                "details": {
                    'summary': event.get('summary'),
                    'meet_link': meet_link,
                    'start': event.get('start', {}).get('dateTime', event.get('start', {}).get('date'))
                }
            }

        else:
            return {"success": False, "message": "Please provide either event_id or summary_search."}

    except Exception as e:
        return {"success": False, "message": f"Failed to retrieve event: {e}"}