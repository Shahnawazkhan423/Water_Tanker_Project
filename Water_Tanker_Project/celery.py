from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module (very important)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Water_Tanker_Project.settings')

app = Celery('Water_Tanker_Project')

# Load config from Django settings, using CELERY_ namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks inside installed apps
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send_mail_every_day': {
        'task': 'Customer.tasks.send_mail_every_day',
        'schedule': crontab(hour=19,minute=0),
    },
}
app.conf.beat_schedule = {
    'send_mail_every_day': {
        'task': 'Supplier.tasks.send_mail_every_day',
        'schedule': crontab(hour=19,minute=0),
    },
}


"""@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
"""