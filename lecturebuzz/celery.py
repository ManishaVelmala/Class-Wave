import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')

app = Celery('lecturebuzz')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    'send-reminders-every-5-minutes': {
        'task': 'reminders.tasks.send_reminders_task',
        'schedule': crontab(minute='*/5'),  # Run every 5 minutes
    },
    'generate-daily-digests': {
        'task': 'reminders.tasks.generate_daily_digests_task',
        'schedule': crontab(hour=0, minute=0),  # Run at midnight every day
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
