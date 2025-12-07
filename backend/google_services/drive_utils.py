# backend/google_services/drive_utils.py
from .gmail_utils import get_google_service
import re

def escape_drive_query(text: str) -> str:
    """
    Escape special characters in Drive API query strings.
    Single quotes must be escaped as \' or wrapped carefully.
    """
    if not text:
        return ""

    text = text.strip()
    text = text.replace("\\", "\\\\")
    text = text.replace("'", "\\'")
    return text

def search_drive_files(query: str, user_email: str = None):
    """
    Searches Google Drive for files matching a query in name or content.

    :param query: Text string to search for in file names or content.
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("drive", "v3", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        escaped_query = escape_drive_query(query)

        if not escaped_query:
            return {"success": False, "message": "Invalid search query."}

        search_query = f"(name contains '{escaped_query}' or fullText contains '{escaped_query}') and trashed = false"

        results = service.files().list(
            q=search_query,
            pageSize=10,
            fields="nextPageToken, files(id, name, webViewLink, mimeType, modifiedTime, owners)",
            orderBy="modifiedTime desc"
        ).execute()

        files = results.get('files', [])

        if not files:
            return {"success": False, "message": f"No files found matching '{query}'."}

        file_list = [{
            "id": file['id'],
            "name": file['name'],
            "link": file.get('webViewLink', ''),
            "mimeType": file.get('mimeType', ''),
            "modified": file.get('modifiedTime', '')
        } for file in files]

        return {
            "success": True,
            "message": f"Found {len(file_list)} files matching '{query}'.",
            "details": file_list
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to search Google Drive: {e}"}


def list_recent_files(limit: int = 10, user_email: str = None):
    """
    Lists the most recently modified files in Google Drive.

    :param limit: Maximum number of files to return (default 10).
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("drive", "v3", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        results = service.files().list(
            q="trashed = false",
            pageSize=limit,
            fields="files(id, name, webViewLink, mimeType, modifiedTime)",
            orderBy="modifiedTime desc"
        ).execute()

        files = results.get('files', [])

        if not files:
            return {"success": False, "message": "No recent files found."}

        file_list = [{
            "id": file['id'],
            "name": file['name'],
            "link": file.get('webViewLink', ''),
            "mimeType": file.get('mimeType', ''),
            "modified": file.get('modifiedTime', '')
        } for file in files]

        return {
            "success": True,
            "message": f"Found {len(file_list)} recent files.",
            "details": file_list
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to list recent files: {e}"}


def get_shareable_link(file_id: str, user_email: str = None):
    """
    Gets a shareable link for a specific file.

    :param file_id: The ID of the file.
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("drive", "v3", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        file = service.files().get(
            fileId=file_id,
            fields="id, name, webViewLink, webContentLink, mimeType"
        ).execute()

        return {
            "success": True,
            "message": f"Retrieved link for '{file.get('name')}'.",
            "details": {
                "id": file.get('id'),
                "name": file.get('name'),
                "webViewLink": file.get('webViewLink', ''),
                "downloadLink": file.get('webContentLink', ''),
                "mimeType": file.get('mimeType', '')
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to get shareable link: {e}"}


def list_files_in_folder(folder_name: str, user_email: str = None):
    """
    Lists files inside a specific folder by searching for the folder name.

    :param folder_name: Name of the folder to search for.
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("drive", "v3", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        escaped_folder_name = escape_drive_query(folder_name)

        if not escaped_folder_name:
            return {"success": False, "message": "Invalid folder name."}

        folder_query = f"name contains '{escaped_folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"

        folder_results = service.files().list(
            q=folder_query,
            pageSize=5,
            fields="files(id, name)"
        ).execute()

        folders = folder_results.get('files', [])

        if not folders:
            return {"success": False, "message": f"No folder found matching '{folder_name}'."}

        # Use the first matching folder
        folder_id = folders[0]['id']
        folder_actual_name = folders[0]['name']

        # Now list files in that folder
        files_query = f"'{folder_id}' in parents and trashed = false"

        files_results = service.files().list(
            q=files_query,
            pageSize=50,
            fields="files(id, name, webViewLink, mimeType, modifiedTime)",
            orderBy="modifiedTime desc"
        ).execute()

        files = files_results.get('files', [])

        if not files:
            return {"success": False, "message": f"No files found in folder '{folder_actual_name}'."}

        file_list = [{
            "id": file['id'],
            "name": file['name'],
            "link": file.get('webViewLink', ''),
            "mimeType": file.get('mimeType', ''),
            "modified": file.get('modifiedTime', '')
        } for file in files]

        return {
            "success": True,
            "message": f"Found {len(file_list)} files in folder '{folder_actual_name}'.",
            "details": {
                "folder_name": folder_actual_name,
                "folder_id": folder_id,
                "files": file_list
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to list files in folder: {e}"}