from background_task import background
from django.utils import timezone
from datetime import timedelta
from rule.models import Rule

@background(schedule=5)
def process_database_task():
    for item in range(10):
        try:
            # پردازش آیتم
            print(f"Processing item {item}")
        except Exception as e:
            print(f"Error processing item {item.id}: {str(e)}")

# تسک با پارامتر
@background(schedule=timedelta(minutes=1))
def another_task(param):
    print(f"Processing with param: {param}")
