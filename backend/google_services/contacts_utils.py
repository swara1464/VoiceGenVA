# backend/google_services/contacts_utils.py
from .gmail_utils import get_google_service

def list_contacts(max_results: int = 20, user_email: str = None):
    """
    Lists contacts from Google Contacts (People API).

    :param max_results: Maximum number of contacts to return.
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("people", "v1", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        results = service.people().connections().list(
            resourceName='people/me',
            pageSize=max_results,
            personFields='names,emailAddresses,phoneNumbers'
        ).execute()

        connections = results.get('connections', [])

        if not connections:
            return {"success": False, "message": "No contacts found."}

        contact_list = []
        for person in connections:
            names = person.get('names', [])
            emails = person.get('emailAddresses', [])
            phones = person.get('phoneNumbers', [])

            name = names[0].get('displayName') if names else 'No Name'
            email = emails[0].get('value') if emails else 'No Email'
            phone = phones[0].get('value') if phones else 'No Phone'

            contact_list.append({
                "name": name,
                "email": email,
                "phone": phone,
                "resource_name": person.get('resourceName')
            })

        return {
            "success": True,
            "message": f"Found {len(contact_list)} contacts.",
            "details": contact_list
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to list contacts: {e}"}


def search_contacts(query: str, user_email: str = None):
    """
    Searches for contacts matching a query.

    :param query: Search query (name or email).
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("people", "v1", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        results = service.people().connections().list(
            resourceName='people/me',
            pageSize=100,
            personFields='names,emailAddresses,phoneNumbers'
        ).execute()

        connections = results.get('connections', [])

        if not connections:
            return {"success": False, "message": "No contacts found."}

        query_lower = query.lower()
        matching_contacts = []

        for person in connections:
            names = person.get('names', [])
            emails = person.get('emailAddresses', [])
            phones = person.get('phoneNumbers', [])

            name = names[0].get('displayName') if names else ''
            email = emails[0].get('value') if emails else ''
            phone = phones[0].get('value') if phones else ''

            if (query_lower in name.lower() or
                query_lower in email.lower()):
                matching_contacts.append({
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "resource_name": person.get('resourceName')
                })

        if not matching_contacts:
            return {"success": False, "message": f"No contacts found matching '{query}'."}

        return {
            "success": True,
            "message": f"Found {len(matching_contacts)} contacts matching '{query}'.",
            "details": matching_contacts
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to search contacts: {e}"}


def get_contact_email(name_query: str, user_email: str = None):
    """
    Gets the email address for a contact by name.
    Useful for auto-completing email recipients.

    :param name_query: Name to search for.
    :param user_email: Email of the user (for token retrieval).
    """
    result = search_contacts(name_query, user_email)

    if not result['success']:
        return result

    contacts = result['details']

    if len(contacts) == 1:
        return {
            "success": True,
            "message": f"Found email for {contacts[0]['name']}.",
            "details": {
                "name": contacts[0]['name'],
                "email": contacts[0]['email']
            }
        }
    else:
        return {
            "success": True,
            "message": f"Found {len(contacts)} possible matches.",
            "details": contacts
        }
