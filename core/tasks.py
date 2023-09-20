from core.models import TimeExpiringPicture
from django.utils import timezone
from celery import shared_task


@shared_task()
def delete_expired_timepictures():
    timepictures = TimeExpiringPicture.objects.filter(expires__lt=timezone.now())
    count = timepictures.count()
    timepictures.delete()
    return f"Deleted {count} objects"
