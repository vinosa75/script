import os
from celery import Celery
 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
 
app = Celery('myproject')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'tasks.create_equity',
        'schedule': 20.0,
    },
}
app.conf.timezone = 'UTC'