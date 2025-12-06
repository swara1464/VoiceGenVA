# backend/google_services/keep_utils.py
"""
Note: Google Keep does not have an official public API.
This implementation uses Google Docs as a workaround to store notes.
Notes are saved as Google Docs in a special "Keep Notes" folder.
"""
from .gmail_utils import get_google_service
from .docs_utils import create_document

def create_note(title: str, content: str, user_email: str = None):
    """
    Creates a note by saving it as a Google Doc in a "Keep Notes" folder.
    This is a workaround since Google Keep has no official API.

    :param title: Note title.
    :param content: Note content.
    :param user_email: Email of the user (for token retrieval).
    """
    drive_service, drive_error = get_google_service("drive", "v3", user_email)
    if drive_error:
        return {"success": False, "message": drive_error}

    try:
        folder_name = "Keep Notes (Vocal Agent)"

        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = drive_service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()

        folders = results.get('files', [])

        if folders:
            folder_id = folders[0]['id']
        else:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = drive_service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            folder_id = folder.get('id')

        doc_result = create_document(title, content, user_email)

        if not doc_result['success']:
            return doc_result

        doc_id = doc_result['details']['doc_id']

        drive_service.files().update(
            fileId=doc_id,
            addParents=folder_id,
            fields='id, parents'
        ).execute()

        return {
            "success": True,
            "message": f"Note '{title}' saved successfully in Keep Notes folder.",
            "details": {
                "note_id": doc_id,
                "note_url": doc_result['details']['doc_url'],
                "folder_id": folder_id
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to create note: {e}"}


def list_notes(max_results: int = 10, user_email: str = None):
    """
    Lists notes from the "Keep Notes" folder.

    :param max_results: Maximum number of notes to return.
    :param user_email: Email of the user (for token retrieval).
    """
    drive_service, error = get_google_service("drive", "v3", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        folder_name = "Keep Notes (Vocal Agent)"

        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = drive_service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()

        folders = results.get('files', [])

        if not folders:
            return {"success": False, "message": "Keep Notes folder not found. Create a note first."}

        folder_id = folders[0]['id']

        query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.document' and trashed=false"
        results = drive_service.files().list(
            q=query,
            pageSize=max_results,
            fields='files(id, name, modifiedTime, webViewLink)',
            orderBy='modifiedTime desc'
        ).execute()

        notes = results.get('files', [])

        if not notes:
            return {"success": False, "message": "No notes found."}

        note_list = [{
            "id": note['id'],
            "title": note['name'],
            "modified": note['modifiedTime'],
            "link": note['webViewLink']
        } for note in notes]

        return {
            "success": True,
            "message": f"Found {len(note_list)} notes.",
            "details": note_list
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to list notes: {e}"}


def delete_note(note_id: str, user_email: str = None):
    """
    Deletes a note (moves it to trash).

    :param note_id: ID of the note to delete.
    :param user_email: Email of the user (for token retrieval).
    """
    drive_service, error = get_google_service("drive", "v3", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        drive_service.files().update(
            fileId=note_id,
            body={'trashed': True}
        ).execute()

        return {
            "success": True,
            "message": "Note deleted successfully.",
            "details": {
                "note_id": note_id
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to delete note: {e}"}
