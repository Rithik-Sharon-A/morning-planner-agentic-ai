"""
Internal task execution service for storing AI-generated tasks.
Replaces Google Calendar integration with Supabase-backed task storage.
"""

import logging
from datetime import datetime, timedelta
from db import supabase

logger = logging.getLogger(__name__)


def convert_time_to_iso(time_str: str, date: datetime = None) -> str:
    """
    Convert time string (e.g. "06:00", "7:00 AM") to ISO 8601 datetime.
    
    Args:
        time_str: Time in HH:MM or "h:mm AM/PM" format
        date: Date to use (defaults to today)
        
    Returns:
        ISO 8601 datetime string
    """
    if date is None:
        date = datetime.now()
    raw = (time_str or "").strip()
    if not raw:
        return date.isoformat()

    try:
        upper = raw.upper()
        is_pm = "PM" in upper
        is_am = "AM" in upper
        if is_pm or is_am:
            # Remove AM/PM and parse
            part = upper.replace("PM", "").replace("AM", "").strip()
            hour, minute = map(int, part.split(":"))
            if is_pm and hour != 12:
                hour += 12
            elif is_am and hour == 12:
                hour = 0
        else:
            hour, minute = map(int, raw.split(":"))
        dt = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return dt.isoformat()
    except Exception as e:
        logger.error(f"Error converting time {time_str}: {e}")
        return date.isoformat()


def save_ai_tasks(user_id: str, events: list[dict], current_date: datetime = None) -> dict:
    """
    Save AI-generated tasks to Supabase ai_tasks table.
    
    Replaces Google Calendar execution with internal task storage.
    
    Args:
        user_id: Authenticated user ID
        events: List of dicts with 'title' (or 'activity') and 'time' keys
        current_date: Date to use for task scheduling (defaults to today)
        
    Returns:
        Dict with status and tasks_created count
    """
    if not user_id:
        return {
            "status": "error",
            "message": "user_id is required",
            "tasks_created": 0
        }
    
    if current_date is None:
        current_date = datetime.now()
    
    created_count = 0
    results = []
    
    for i, event in enumerate(events):
        # Support both 'title' and 'activity' keys
        task_title = event.get("title") or event.get("activity", "Task")
        time_str = event.get("time", "")
        
        if not time_str:
            continue
        
        # Convert start time
        start_time = convert_time_to_iso(time_str, current_date)
        
        # Calculate end time from next event or default to 1 hour later
        if i < len(events) - 1:
            next_time_str = events[i + 1].get("time", "")
            if next_time_str:
                end_time = convert_time_to_iso(next_time_str, current_date)
            else:
                end_dt = datetime.fromisoformat(start_time) + timedelta(hours=1)
                end_time = end_dt.isoformat()
        else:
            # Last event: default to 23:59
            end_time = convert_time_to_iso("23:59", current_date)
        
        # Save task to Supabase
        try:
            result = supabase.table("ai_tasks").insert({
                "user_id": user_id,
                "task": task_title,
                "start_time": start_time,
                "end_time": end_time,
                "status": "pending",
            }).execute()
            
            if result.data:
                created_count += 1
                results.append({
                    "task_id": result.data[0].get("id"),
                    "task": task_title,
                    "start_time": start_time,
                    "end_time": end_time,
                    "status": "pending",
                })
                logger.info(f"Task created: {task_title} at {start_time}")
        except Exception as e:
            logger.exception(f"Failed to create task: {e}")
            continue
    
    return {
        "status": "success",
        "tasks_created": created_count,
        "results": results
    }


def get_user_tasks(user_id: str, status: str = None) -> list[dict]:
    """
    Fetch AI tasks for a user from Supabase.
    
    Args:
        user_id: User ID
        status: Optional status filter ('pending', 'completed', 'cancelled')
        
    Returns:
        List of task dicts
    """
    if not user_id:
        return []
    
    try:
        query = supabase.table("ai_tasks").select("*").eq("user_id", user_id)
        
        if status:
            query = query.eq("status", status)
        
        result = query.order("start_time", desc=False).execute()
        return result.data if result.data else []
    except Exception as e:
        logger.exception(f"Failed to fetch tasks for user {user_id}: {e}")
        return []


def complete_task(task_id: str, user_id: str) -> dict:
    """
    Mark a task as completed.
    
    Args:
        task_id: Task UUID
        user_id: User ID (for security verification)
        
    Returns:
        Dict with status and updated task data
    """
    if not task_id or not user_id:
        return {"status": "error", "message": "task_id and user_id are required"}
    
    try:
        # Update task status to completed (verify user_id for security)
        result = supabase.table("ai_tasks").update({
            "status": "completed"
        }).eq("id", task_id).eq("user_id", user_id).execute()
        
        if not result.data:
            return {"status": "error", "message": "Task not found or unauthorized"}
        
        logger.info(f"Task {task_id} marked as completed by user {user_id}")
        return {"status": "success", "task": result.data[0]}
    except Exception as e:
        logger.exception(f"Failed to complete task {task_id}: {e}")
        return {"status": "error", "message": str(e)}


def delete_user_tasks(user_id: str) -> bool:
    """
    Delete all tasks for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        True if successful
    """
    if not user_id:
        return False
    
    try:
        supabase.table("ai_tasks").delete().eq("user_id", user_id).execute()
        logger.info(f"Deleted all tasks for user {user_id}")
        return True
    except Exception as e:
        logger.exception(f"Failed to delete tasks for user {user_id}: {e}")
        return False
