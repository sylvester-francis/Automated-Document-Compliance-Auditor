"""
Background task processing utilities.
"""
import threading
import uuid
import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

# Store for background tasks
_tasks = {}

class TaskStatus:
    """Task status constants."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class BackgroundTask:
    """Background task representation."""
    def __init__(self, task_id, name, status=TaskStatus.PENDING):
        self.task_id = task_id
        self.name = name
        self.status = status
        self.result = None
        self.error = None
        self.progress = 0
        self.start_time = None
        self.end_time = None
        self.created_at = time.time()

    def to_dict(self):
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "progress": self.progress,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "created_at": self.created_at,
            "duration": (self.end_time - self.start_time) if self.end_time and self.start_time else None
        }

def run_in_background(name):
    """
    Decorator to run a function in the background.
    
    Args:
        name: Name of the task
    
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            task_id = str(uuid.uuid4())
            task = BackgroundTask(task_id, name)
            _tasks[task_id] = task
            
            def target():
                task.status = TaskStatus.RUNNING
                task.start_time = time.time()
                try:
                    # Run the function
                    result = func(*args, **kwargs)
                    task.result = result
                    task.status = TaskStatus.COMPLETED
                except Exception as e:
                    logger.exception(f"Background task {task_id} failed")
                    task.error = str(e)
                    task.status = TaskStatus.FAILED
                finally:
                    task.end_time = time.time()
            
            # Start the thread
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            
            return task_id
        return wrapper
    return decorator

def get_task(task_id):
    """
    Get a task by ID.
    
    Args:
        task_id: ID of the task
    
    Returns:
        Task object or None if not found
    """
    return _tasks.get(task_id)

def get_task_status(task_id):
    """
    Get the status of a task.
    
    Args:
        task_id: ID of the task
    
    Returns:
        Task status dictionary or None if not found
    """
    task = _tasks.get(task_id)
    if task:
        return task.to_dict()
    return None

def update_task_progress(task_id, progress):
    """
    Update the progress of a task.
    
    Args:
        task_id: ID of the task
        progress: Progress value (0-100)
    """
    task = _tasks.get(task_id)
    if task:
        task.progress = progress

def clean_old_tasks(max_age=86400):  # Default: 24 hours
    """
    Clean up old completed tasks.
    
    Args:
        max_age: Maximum age in seconds
    """
    current_time = time.time()
    to_remove = []
    
    for task_id, task in _tasks.items():
        if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
            if current_time - task.created_at > max_age:
                to_remove.append(task_id)
    
    for task_id in to_remove:
        del _tasks[task_id]
    
    logger.info(f"Cleaned up {len(to_remove)} old tasks")
