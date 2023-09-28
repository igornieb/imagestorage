from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from core.models import Account, User, Tier, Picture
import os


@receiver(post_save, sender=User)
def create_account(sender, instance: User, created, **kwargs):
    if created:
        tier = Tier.objects.get(name="Basic")
        Account.objects.create(user=instance, tier=tier)


@receiver(post_delete, sender=Picture)
def delete_file_on_model_delete(sender, instance: Picture, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.img:
        if os.path.isfile(instance.img.path):
            os.remove(instance.img.path)


@receiver(pre_save, sender=Picture)
def delete_file_on_img_edit(sender, instance: Picture, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    try:
        old_file = Picture.objects.get(pk=instance.pk).img
    except Picture.DoesNotExist:
        return False

    new_file = instance.img
    if old_file != new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
