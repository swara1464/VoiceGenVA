# backend/google_services/drive_utils.py
from .gmail_utils import get_google_service # Reuse the auth function

def search_drive_files(query: str, user_email: str = None):
    """
    Searches Google Drive for files matching a query.

    :param query: Text string to search for in file names or content.
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("drive", "v3", user_email)
    if error:
        return {"success": False, "message": error}
        
    try:
        # Build the search query string
        # This searches file names and content, excluding trashed files
        search_query = f"name contains '{query}' or fullText contains '{query}' and trashed = false"

        results = service.files().list(
            q=search_query,
            pageSize=5, # Limit to 5 results for brevity
            fields="nextPageToken, files(id, name, webViewLink, mimeType)"
        ).execute()

        files = results.get('files', [])
        
        if not files:
            return {"success": False, "message": f"No files found matching '{query}'."}
        
        file_list = [{
            "id": file['id'],
            "name": file['name'],
            "link": file['webViewLink'],
            "mimeType": file['mimeType']
        } for file in files]
        
        return {
            "success": True,
            "message": f"Found {len(file_list)} files matching '{query}'.",
            "details": file_list
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to search Google Drive: {e}"}