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
    Includes both owned and shared files.

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

        # Search in name only for better relevance, include both owned and shared
        search_query = f"name contains '{escaped_query}' and trashed = false"

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


def upload_file(file_name: str, file_content: bytes, mime_type: str = 'text/plain', folder_id: str = None, user_email: str = None):
    """
    Uploads a file to Google Drive.

    :param file_name: Name of the file to create.
    :param file_content: Binary content of the file.
    :param mime_type: MIME type of the file (default: 'text/plain').
    :param folder_id: Optional folder ID to upload to (default: root).
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("drive", "v3", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        from googleapiclient.http import MediaInMemoryUpload

        file_metadata = {'name': file_name}
        if folder_id:
            file_metadata['parents'] = [folder_id]

        media = MediaInMemoryUpload(file_content, mimetype=mime_type, resumable=True)

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink'
        ).execute()

        return {
            "success": True,
            "message": f"File '{file_name}' uploaded successfully.",
            "details": {
                "file_id": file.get('id'),
                "file_name": file.get('name'),
                "file_link": file.get('webViewLink')
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to upload file: {e}"}


def delete_file(file_id: str, user_email: str = None):
    """
    Deletes a file from Google Drive (moves to trash).

    :param file_id: The ID of the file to delete.
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("drive", "v3", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        service.files().delete(fileId=file_id).execute()

        return {
            "success": True,
            "message": f"File deleted successfully.",
            "details": {
                "file_id": file_id
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to delete file: {e}"}


def rename_file(file_id: str, new_name: str, user_email: str = None):
    """
    Renames a file in Google Drive.

    :param file_id: The ID of the file to rename.
    :param new_name: The new name for the file.
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("drive", "v3", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        file_metadata = {'name': new_name}

        updated_file = service.files().update(
            fileId=file_id,
            body=file_metadata,
            fields='id, name, webViewLink'
        ).execute()

        return {
            "success": True,
            "message": f"File renamed to '{new_name}' successfully.",
            "details": {
                "file_id": updated_file.get('id'),
                "new_name": updated_file.get('name'),
                "file_link": updated_file.get('webViewLink')
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to rename file: {e}"}


def share_file(file_id: str, email: str, role: str = 'reader', user_email: str = None):
    """
    Shares a file with a specific email address.

    :param file_id: The ID of the file to share.
    :param email: Email address to share with.
    :param role: Permission role ('reader', 'writer', 'commenter').
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("drive", "v3", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        permission = {
            'type': 'user',
            'role': role,
            'emailAddress': email
        }

        service.permissions().create(
            fileId=file_id,
            body=permission,
            fields='id, emailAddress, role'
        ).execute()

        # Get file info
        file = service.files().get(
            fileId=file_id,
            fields='id, name, webViewLink'
        ).execute()

        return {
            "success": True,
            "message": f"File '{file.get('name')}' shared with {email} as {role}.",
            "details": {
                "file_id": file.get('id'),
                "file_name": file.get('name'),
                "file_link": file.get('webViewLink'),
                "shared_with": email,
                "role": role
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to share file: {e}"}


def list_files_in_folder(folder_name: str, user_email: str = None):
    """
    Lists files inside a specific folder by searching for the folder name.
    Also searches for files if folder not found.

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

        # First try to find a folder
        folder_query = f"name contains '{escaped_folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"

        folder_results = service.files().list(
            q=folder_query,
            pageSize=5,
            fields="files(id, name)"
        ).execute()

        folders = folder_results.get('files', [])

        if folders:
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
        else:
            # No folder found, search for files instead
            return search_drive_files(folder_name, user_email)

    except Exception as e:
        return {"success": False, "message": f"Failed to list files in folder: {e}"}