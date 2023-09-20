from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_base_tiers(**kwargs):
    from core.models import Tier, FileHeight
    try:
        try:
            FileHeight.objects.create(size=200)
            FileHeight.objects.create(size=400)
        except Exception as e:
            print(e)
        f_200 = FileHeight.objects.get(size=200)
        f_400 = FileHeight.objects.get(size=400)
        # basic tier
        basic = Tier.objects.create(name="Basic")
        basic.sizes_allowed.add(f_200)
        basic.save()
        # premium
        premium = Tier.objects.create(name="Premium", allow_original=True)
        premium.sizes_allowed.add(f_200, f_400)
        premium.save()
        # enterprise
        enterprise = Tier.objects.create(name="Enterprise", allow_original=True,
                                         allow_creating_time_expiring_link=True)
        enterprise.sizes_allowed.add(f_200, f_400)
        enterprise.save()
        print("Tiers created")
    except Exception as e:
        print(e)


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        post_migrate.connect(create_base_tiers, sender=self)
        import core.signals
