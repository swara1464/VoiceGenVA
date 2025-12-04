# backend/google_services/sheets_utils.py
from .gmail_utils import get_google_service

def create_spreadsheet(title: str):
    """
    Creates a new Google Spreadsheet with the specified title.

    :param title: Spreadsheet title.
    """
    service, error = get_google_service("sheets", "v4")
    if error:
        return {"success": False, "message": error}

    try:
        spreadsheet = {
            'properties': {
                'title': title
            }
        }

        spreadsheet = service.spreadsheets().create(
            body=spreadsheet,
            fields='spreadsheetId'
        ).execute()

        sheet_id = spreadsheet.get('spreadsheetId')
        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"

        return {
            "success": True,
            "message": f"Spreadsheet '{title}' created successfully.",
            "details": {
                "sheet_id": sheet_id,
                "sheet_url": sheet_url
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to create spreadsheet: {e}"}


def add_row_to_sheet(sheet_id: str, range_name: str, values: list):
    """
    Appends a row of data to a Google Sheet.

    :param sheet_id: The ID of the spreadsheet.
    :param range_name: The A1 notation of the range (e.g., 'Sheet1!A:D').
    :param values: List of values to append (e.g., ['John', 'Doe', 'john@example.com']).
    """
    service, error = get_google_service("sheets", "v4")
    if error:
        return {"success": False, "message": error}

    try:
        body = {
            'values': [values]
        }

        result = service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()

        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"

        return {
            "success": True,
            "message": f"Row added to spreadsheet successfully.",
            "details": {
                "sheet_id": sheet_id,
                "sheet_url": sheet_url,
                "updated_range": result.get('updates').get('updatedRange'),
                "updated_rows": result.get('updates').get('updatedRows')
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to add row to sheet: {e}"}


def read_sheet_data(sheet_id: str, range_name: str):
    """
    Reads data from a Google Sheet.

    :param sheet_id: The ID of the spreadsheet.
    :param range_name: The A1 notation of the range to read (e.g., 'Sheet1!A1:D10').
    """
    service, error = get_google_service("sheets", "v4")
    if error:
        return {"success": False, "message": error}

    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=range_name
        ).execute()

        values = result.get('values', [])

        if not values:
            return {"success": False, "message": "No data found in the specified range."}

        return {
            "success": True,
            "message": f"Successfully read {len(values)} rows from sheet.",
            "details": {
                "sheet_id": sheet_id,
                "range": range_name,
                "data": values
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to read sheet data: {e}"}


def update_sheet_cell(sheet_id: str, range_name: str, value: str):
    """
    Updates a specific cell or range in a Google Sheet.

    :param sheet_id: The ID of the spreadsheet.
    :param range_name: The A1 notation of the cell/range (e.g., 'Sheet1!A1').
    :param value: The new value for the cell.
    """
    service, error = get_google_service("sheets", "v4")
    if error:
        return {"success": False, "message": error}

    try:
        body = {
            'values': [[value]]
        }

        result = service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()

        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"

        return {
            "success": True,
            "message": f"Cell updated successfully.",
            "details": {
                "sheet_id": sheet_id,
                "sheet_url": sheet_url,
                "updated_range": result.get('updatedRange'),
                "updated_cells": result.get('updatedCells')
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to update cell: {e}"}
