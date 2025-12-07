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


def read_document(doc_id: str, user_email: str = None):
    """
    Reads the content of a Google Document.

    :param doc_id: The ID of the document to read.
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("docs", "v1", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        doc = service.documents().get(documentId=doc_id).execute()
        title = doc.get('title', 'Untitled')
        body_content = doc.get('body').get('content', [])

        # Extract text from paragraphs
        text_content = []
        for element in body_content:
            if 'paragraph' in element:
                paragraph = element.get('paragraph')
                for elem in paragraph.get('elements', []):
                    if 'textRun' in elem:
                        text_content.append(elem['textRun']['content'])

        full_text = ''.join(text_content)
        doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

        return {
            "success": True,
            "message": f"Document '{title}' read successfully.",
            "details": {
                "doc_id": doc_id,
                "title": title,
                "content": full_text,
                "doc_url": doc_url
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to read document: {e}"}


def format_text_range(doc_id: str, start_index: int, end_index: int, bold: bool = None,
                      italic: bool = None, underline: bool = None, font_size: int = None, user_email: str = None):
    """
    Applies formatting to a specific text range in a Google Document.

    :param doc_id: The ID of the document.
    :param start_index: Start index of the text range.
    :param end_index: End index of the text range.
    :param bold: Apply bold formatting (True/False).
    :param italic: Apply italic formatting (True/False).
    :param underline: Apply underline formatting (True/False).
    :param font_size: Font size in points.
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("docs", "v1", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        requests = []
        text_style = {}

        if bold is not None:
            text_style['bold'] = bold
        if italic is not None:
            text_style['italic'] = italic
        if underline is not None:
            text_style['underline'] = underline
        if font_size is not None:
            text_style['fontSize'] = {'magnitude': font_size, 'unit': 'PT'}

        if text_style:
            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': start_index,
                        'endIndex': end_index
                    },
                    'textStyle': text_style,
                    'fields': ','.join(text_style.keys())
                }
            })

        if not requests:
            return {"success": False, "message": "No formatting changes specified"}

        service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

        doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

        return {
            "success": True,
            "message": f"Text formatting applied successfully.",
            "details": {
                "doc_id": doc_id,
                "doc_url": doc_url,
                "formatted_range": f"{start_index}-{end_index}"
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to format text: {e}"}


def replace_text_in_document(doc_id: str, find_text: str, replace_text: str, user_email: str = None):
    """
    Finds and replaces text in a Google Document.
    Useful for editing specific paragraphs or sections.

    :param doc_id: The ID of the document.
    :param find_text: Text to find in the document.
    :param replace_text: Text to replace it with.
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("docs", "v1", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        requests = [
            {
                'replaceAllText': {
                    'containsText': {
                        'text': find_text,
                        'matchCase': False
                    },
                    'replaceText': replace_text
                }
            }
        ]

        result = service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

        replacements = result.get('replies', [{}])[0].get('replaceAllText', {}).get('occurrencesChanged', 0)
        doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

        return {
            "success": True,
            "message": f"Replaced {replacements} occurrence(s) of '{find_text}'.",
            "details": {
                "doc_id": doc_id,
                "doc_url": doc_url,
                "occurrences_changed": replacements
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to replace text: {e}"}


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
