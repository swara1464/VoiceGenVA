# backend/google_services/calendar_utils.py
from .gmail_utils import get_google_service
from datetime import datetime, timedelta
import pytz
from logs.log_utils import log_execution

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


def create_instant_meet(title: str = "Google Meet", attendees: list = None, user_email: str = None, timezone: str = "UTC"):
    """
    Create an instant Google Meet event starting now and ending in 1 hour.

    :param title: Meeting title (default: "Google Meet")
    :param attendees: List of attendee email addresses
    :param user_email: Email of the user (for token retrieval)
    :param timezone: Timezone for the event (default: UTC)
    """
    service, error = get_google_service("calendar", "v3", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        now = datetime.now(pytz.timezone(timezone))
        start_time = now.isoformat()
        end_time = (now + timedelta(hours=1)).isoformat()

        event = {
            'summary': title,
            'description': 'Instant meeting created via voice agent',
            'start': {'dateTime': start_time, 'timeZone': timezone},
            'end': {'dateTime': end_time, 'timeZone': timezone},
            'conferenceData': {
                'createRequest': {
                    'requestId': f'instant-meet-{int(datetime.now().timestamp())}',
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'},
                },
            },
            'attendees': [{'email': email} for email in attendees] if attendees else [],
            'reminders': {'useDefault': True},
        }

        created_event = service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1
        ).execute()

        meet_link = created_event.get('hangoutLink')

        if user_email:
            log_execution(user_email, "CALENDAR_INSTANT_MEET", "CREATED", {
                "title": title,
                "attendees_count": len(attendees) if attendees else 0,
                "meet_link": meet_link
            })

        return {
            "success": True,
            "message": f"Instant meeting '{title}' created. Meet link: {meet_link}",
            "details": {
                "event_id": created_event.get('id'),
                "meet_link": meet_link,
                "title": title,
                "start": start_time,
                "end": end_time
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to create instant meet: {e}"}


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


def delete_calendar_event(event_id: str = None, summary: str = None, user_email: str = None):
    """
    Deletes a calendar event by ID or title.

    :param event_id: ID of the event to delete (optional if summary provided)
    :param summary: Title of event to search and delete (optional if event_id provided)
    :param user_email: Email of the user (for token retrieval)
    """
    service, error = get_google_service("calendar", "v3", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        # If no event_id, search by summary
        if not event_id and summary:
            now = datetime.now().isoformat() + 'Z'

            events_result = service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=50,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            matching_event = None

            for event in events:
                if summary.lower() in event.get('summary', '').lower():
                    matching_event = event
                    break

            if not matching_event:
                return {"success": False, "message": f"No event found with title '{summary}'"}

            event_id = matching_event['id']

        if not event_id:
            return {"success": False, "message": "No event_id or summary provided"}

        service.events().delete(calendarId='primary', eventId=event_id).execute()

        if user_email:
            log_execution(user_email, "CALENDAR_DELETE", "SUCCESS", {
                "event_id": event_id
            })

        return {
            "success": True,
            "message": f"Event deleted successfully",
            "details": {
                "event_id": event_id
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to delete event: {e}"}