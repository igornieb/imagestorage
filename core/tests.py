from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from datetime import timedelta
from core.models import Account, Tier, Picture, TimeExpiringPicture, FileHeight


class AccountModelTest(TestCase):
    def setUp(cls):
        User.objects.create(username='testuser')

    def test_if_account_exist(self):
        # tests if accoutnt was created by signal
        account = Account.objects.filter(user=User.objects.get(username='testuser')).exists()
        self.assertEqual(True, account)


class TierModelTest(TestCase):
    def setUp(cls):
        # creates test tier
        t = Tier.objects.create(name="TestTier")
        f_1 = FileHeight.objects.get(size=200)
        f_2 = FileHeight.objects.create(size=300)
        f_3 = FileHeight.objects.create(size=800)
        t.sizes_allowed.add(f_1, f_2, f_3)
        t.save()

    def test_if_default_tiers_exists(self):
        # test if default tiers exists
        tiers = Tier.objects.filter(name="Basic").exists() and Tier.objects.filter(
            name="Premium").exists() and Tier.objects.filter(name="Enterprise").exists()
        self.assertEqual(True, tiers)


class PictureModelTest(TestCase):
    def setUp(cls):
        t = Tier.objects.create(name="TestTier")
        t.save()
        f_1 = FileHeight.objects.get(size=200)
        f_2 = FileHeight.objects.create(size=300)
        t.sizes_allowed.add(f_1, f_2)
        t.save()
        u = User.objects.create(username='testuser')
        a = Account.objects.get(user=u)
        a.tier = t
        a.save()
        Picture.objects.create(name="TestPicture", img="", owner=a)

    def test_str_representation(self):
        picture = Picture.objects.filter(name="TestPicture").first()
        expected_object_name = f'{picture.name} - {picture.owner}'
        self.assertEqual(str(picture), expected_object_name)

    def test_get_absolute_url(self):
        picture = Picture.objects.filter(name="TestPicture").first()
        expected_urls = [
            reverse("picture-details", kwargs={'pk': picture.pk, "height": 200}),
            reverse("picture-details", kwargs={'pk': picture.pk, "height": 300})
        ]
        self.assertEqual(picture.get_absolute_url(), expected_urls)


class TimePictureModelTest(TestCase):
    def setUp(self):
        u = User.objects.create(username='testuser')
        a = Account.objects.get(user=u)
        self.picture = Picture.objects.create(name="TestPicture", img="", owner=a)
        TimeExpiringPicture.objects.create(picture=self.picture, time=400)

    def test_validation_time_field_error(self):
        invalid_times = [299, 30001, 20]
        with self.assertRaises(ValidationError):
            for time in invalid_times:
                picture1 = TimeExpiringPicture(picture=self.picture, time=time)
                picture1.full_clean()

    def test_validation_time_field(self):
        valid_times = [400, 3000, 300]
        for time in valid_times:
            picture1 = TimeExpiringPicture(picture=self.picture, time=time)
            picture1.full_clean()

    def test_str_representation(self):
        picture = TimeExpiringPicture.objects.filter(picture=self.picture).first()
        expected_object_name = f'{picture.picture} {picture.created} {picture.expires}'
        self.assertEqual(str(picture), expected_object_name)

    def test_get_absolute_url(self):
        picture = TimeExpiringPicture.objects.filter(picture=self.picture).first()
        expected_urls = reverse("picture-time-link", kwargs={'pk': picture.pk})
        self.assertEqual(picture.get_absolute_url(), expected_urls)

    def test_get_expires_field(self):
        picture = TimeExpiringPicture.objects.filter(picture=self.picture).first()
        expected_expires = picture.expires
        self.assertEqual(picture.created + timedelta(seconds=picture.time), expected_expires)
