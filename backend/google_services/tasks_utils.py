# backend/google_services/tasks_utils.py
from .gmail_utils import get_google_service

def list_task_lists(user_email: str = None):
    """
    Lists all task lists for the authenticated user.
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("tasks", "v1", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        results = service.tasklists().list().execute()
        task_lists = results.get('items', [])

        if not task_lists:
            return {"success": False, "message": "No task lists found."}

        list_data = [{
            "id": tl['id'],
            "title": tl['title']
        } for tl in task_lists]

        return {
            "success": True,
            "message": f"Found {len(list_data)} task lists.",
            "details": list_data
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to list task lists: {e}"}


def create_task(title: str, notes: str = "", due_date: str = None, tasklist_id: str = "@default", user_email: str = None):
    """
    Creates a new task in the specified task list.

    :param title: Task title.
    :param notes: Task notes/description.
    :param due_date: Due date in RFC 3339 format (e.g., '2025-12-15T00:00:00Z').
    :param tasklist_id: ID of the task list (defaults to '@default').
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("tasks", "v1", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        task = {
            'title': title,
            'notes': notes
        }

        if due_date:
            task['due'] = due_date

        result = service.tasks().insert(
            tasklist=tasklist_id,
            body=task
        ).execute()

        return {
            "success": True,
            "message": f"Task '{title}' created successfully.",
            "details": {
                "task_id": result.get('id'),
                "title": result.get('title'),
                "status": result.get('status')
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to create task: {e}"}


def list_tasks(tasklist_id: str = "@default", max_results: int = 10, user_email: str = None):
    """
    Lists tasks from a specific task list.

    :param tasklist_id: ID of the task list (defaults to '@default').
    :param max_results: Maximum number of tasks to return.
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("tasks", "v1", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        results = service.tasks().list(
            tasklist=tasklist_id,
            maxResults=max_results
        ).execute()

        tasks = results.get('items', [])

        if not tasks:
            return {"success": False, "message": "No tasks found in this list."}

        task_data = [{
            "id": task['id'],
            "title": task['title'],
            "status": task.get('status', 'needsAction'),
            "notes": task.get('notes', ''),
            "due": task.get('due', 'No due date')
        } for task in tasks]

        return {
            "success": True,
            "message": f"Found {len(task_data)} tasks.",
            "details": task_data
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to list tasks: {e}"}


def complete_task(task_id: str, tasklist_id: str = "@default", user_email: str = None):
    """
    Marks a task as completed.

    :param task_id: ID of the task to complete.
    :param tasklist_id: ID of the task list (defaults to '@default').
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("tasks", "v1", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        task = service.tasks().get(
            tasklist=tasklist_id,
            task=task_id
        ).execute()

        task['status'] = 'completed'

        result = service.tasks().update(
            tasklist=tasklist_id,
            task=task_id,
            body=task
        ).execute()

        return {
            "success": True,
            "message": f"Task '{result.get('title')}' marked as completed.",
            "details": {
                "task_id": result.get('id'),
                "title": result.get('title'),
                "status": result.get('status')
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to complete task: {e}"}


def delete_task(task_id: str, tasklist_id: str = "@default", user_email: str = None):
    """
    Deletes a task.

    :param task_id: ID of the task to delete.
    :param tasklist_id: ID of the task list (defaults to '@default').
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("tasks", "v1", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        service.tasks().delete(
            tasklist=tasklist_id,
            task=task_id
        ).execute()

        return {
            "success": True,
            "message": f"Task deleted successfully.",
            "details": {
                "task_id": task_id
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to delete task: {e}"}


def update_task(task_id: str, title: str = None, notes: str = None, due_date: str = None,
                status: str = None, tasklist_id: str = "@default", user_email: str = None):
    """
    Updates an existing task with new information.

    :param task_id: ID of the task to update.
    :param title: New task title (optional).
    :param notes: New task notes (optional).
    :param due_date: New due date in RFC 3339 format (optional).
    :param status: New status ('needsAction' or 'completed') (optional).
    :param tasklist_id: ID of the task list (defaults to '@default').
    :param user_email: Email of the user (for token retrieval).
    """
    service, error = get_google_service("tasks", "v1", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        # Get the current task
        task = service.tasks().get(
            tasklist=tasklist_id,
            task=task_id
        ).execute()

        # Update only the provided fields
        if title is not None:
            task['title'] = title
        if notes is not None:
            task['notes'] = notes
        if due_date is not None:
            task['due'] = due_date
        if status is not None:
            task['status'] = status

        # Update the task
        result = service.tasks().update(
            tasklist=tasklist_id,
            task=task_id,
            body=task
        ).execute()

        return {
            "success": True,
            "message": f"Task '{result.get('title')}' updated successfully.",
            "details": {
                "task_id": result.get('id'),
                "title": result.get('title'),
                "status": result.get('status'),
                "notes": result.get('notes', ''),
                "due": result.get('due', 'No due date')
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to update task: {e}"}
