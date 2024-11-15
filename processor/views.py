from .tasks import process_database_task, another_task
from django.http import JsonResponse

def start_tasks(request):
    # شروع تسک اول - تکرار هر 60 ثانیه
    process_database_task(repeat=60)
    
    # شروع تسک دوم - تکرار هر 5 دقیقه
    another_task("test_param", repeat=300)
    
    return JsonResponse({"status": "Tasks scheduled"})