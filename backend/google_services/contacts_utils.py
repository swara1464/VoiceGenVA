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


def create_contact(given_name: str = None, family_name: str = None, name: str = None, email: str = None, phone: str = None, user_email: str = None):
    """
    Creates a new contact in Google Contacts.
    NOTE: Requires 'contacts' scope (not just contacts.readonly).

    :param given_name: Contact's first name.
    :param family_name: Contact's last name.
    :param name: Contact's full name (alternative to given_name/family_name).
    :param email: Contact's email address (optional).
    :param phone: Contact's phone number (optional).
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("people", "v1", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        # Build name structure
        name_obj = {}
        if given_name:
            name_obj['givenName'] = given_name
        if family_name:
            name_obj['familyName'] = family_name
        if name and not given_name and not family_name:
            name_obj['givenName'] = name

        contact_data = {
            'names': [name_obj]
        }

        if email:
            contact_data['emailAddresses'] = [{'value': email}]

        if phone:
            contact_data['phoneNumbers'] = [{'value': phone}]

        result = service.people().createContact(
            body=contact_data
        ).execute()

        full_name = f"{given_name or ''} {family_name or ''}".strip() or name or "New Contact"

        return {
            "success": True,
            "message": f"Contact '{full_name}' created successfully.",
            "details": {
                "resource_name": result.get('resourceName'),
                "name": full_name,
                "email": email,
                "phone": phone
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to create contact: {e}"}


def update_contact(resource_name: str, name: str = None, email: str = None, phone: str = None, user_email: str = None):
    """
    Updates an existing contact in Google Contacts.
    NOTE: Requires 'contacts' scope (not just contacts.readonly).

    :param resource_name: The resource name of the contact (e.g., 'people/c1234567890').
    :param name: New name for the contact (optional).
    :param email: New email for the contact (optional).
    :param phone: New phone for the contact (optional).
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("people", "v1", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        # Get current contact data
        current_contact = service.people().get(
            resourceName=resource_name,
            personFields='names,emailAddresses,phoneNumbers,etag'
        ).execute()

        # Build update data
        contact_data = {
            'etag': current_contact.get('etag'),
            'names': current_contact.get('names', []),
            'emailAddresses': current_contact.get('emailAddresses', []),
            'phoneNumbers': current_contact.get('phoneNumbers', [])
        }

        # Update fields if provided
        if name:
            contact_data['names'] = [{'givenName': name}]

        if email:
            contact_data['emailAddresses'] = [{'value': email}]

        if phone:
            contact_data['phoneNumbers'] = [{'value': phone}]

        result = service.people().updateContact(
            resourceName=resource_name,
            updatePersonFields='names,emailAddresses,phoneNumbers',
            body=contact_data
        ).execute()

        return {
            "success": True,
            "message": f"Contact updated successfully.",
            "details": {
                "resource_name": result.get('resourceName')
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to update contact: {e}"}


def delete_contact(resource_name: str, user_email: str = None):
    """
    Deletes a contact from Google Contacts.
    NOTE: Requires 'contacts' scope (not just contacts.readonly).

    :param resource_name: The resource name of the contact to delete (e.g., 'people/c1234567890').
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("people", "v1", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        service.people().deleteContact(resourceName=resource_name).execute()

        return {
            "success": True,
            "message": f"Contact deleted successfully.",
            "details": {
                "resource_name": resource_name
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to delete contact: {e}"}
