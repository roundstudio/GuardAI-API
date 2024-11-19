import threading
from django.conf import settings
from .tasks import process_database_task

def start():
    if not settings.DEBUG or not hasattr(start, '_started'):
        start._started = True
        thread = threading.Thread(target=run_tasks, daemon=True)
        thread.start()

def run_tasks():
    # کد اصلی تسک اینجا
    # process_database_task()
    pass