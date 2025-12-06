# backend/google_services/docs_utils.py
from .gmail_utils import get_google_service

def create_document(title: str, content: str = "", user_email: str = None):
    """
    Creates a new Google Doc with the specified title and optional initial content.

    :param title: Document title.
    :param content: Initial document content.
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("docs", "v1", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        doc = service.documents().create(body={"title": title}).execute()
        doc_id = doc.get('documentId')

        if content:
            requests = [
                {
                    'insertText': {
                        'location': {'index': 1},
                        'text': content
                    }
                }
            ]

            service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()

        doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

        return {
            "success": True,
            "message": f"Document '{title}' created successfully.",
            "details": {
                "doc_id": doc_id,
                "doc_url": doc_url
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to create document: {e}"}


def append_to_document(doc_id: str, content: str, user_email: str = None):
    """
    Appends content to an existing Google Doc.

    :param doc_id: The ID of the document to append to.
    :param content: Text content to append.
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("docs", "v1", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        doc = service.documents().get(documentId=doc_id).execute()
        doc_content = doc.get('body').get('content')
        end_index = doc_content[-1].get('endIndex', 1) - 1

        requests = [
            {
                'insertText': {
                    'location': {'index': end_index},
                    'text': f"\n{content}"
                }
            }
        ]

        service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

        doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

        return {
            "success": True,
            "message": f"Content appended to document successfully.",
            "details": {
                "doc_id": doc_id,
                "doc_url": doc_url
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to append to document: {e}"}


def search_documents(query: str, user_email: str = None):
    """
    Searches for Google Docs files in Drive that match the query.
    This uses the Drive API to search specifically for Google Docs.

    :param query: Search query string.
    :param user_email: Email of the user (for token retrieval).
    """
    drive_service, error = get_google_service("drive", "v3", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        search_query = f"name contains '{query}' and mimeType = 'application/vnd.google-apps.document' and trashed = false"

        results = drive_service.files().list(
            q=search_query,
            pageSize=5,
            fields="nextPageToken, files(id, name, webViewLink)"
        ).execute()

        files = results.get('files', [])

        if not files:
            return {"success": False, "message": f"No documents found matching '{query}'."}

        file_list = [{
            "id": file['id'],
            "name": file['name'],
            "link": file['webViewLink']
        } for file in files]

        return {
            "success": True,
            "message": f"Found {len(file_list)} documents matching '{query}'.",
            "details": file_list
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to search documents: {e}"}
