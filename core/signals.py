from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import Account, User, Tier


@receiver(post_save, sender=User)
def create_account(sender, instance, created, **kwargs):
    if created:
        tier = Tier.objects.get(name="Basic")
        Account.objects.create(user=instance, tier=tier)
