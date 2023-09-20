import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imagestorage.settings')

app = Celery('app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'delete_expired_timepictures-every-10-minutes': {
        'task': 'core.tasks.delete_expired_timepictures',
        'schedule': 10*60,
    }
}
