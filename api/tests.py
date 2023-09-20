from django.urls import resolve
from rest_framework.test import APITestCase
from api.views import *
from api.urls import TokenObtainPairView, TokenRefreshView
from core.models import *
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile


class UrlsTest(APITestCase):

    # Tests if all api urls are resolved correctly
    def test_pictures_url(self):
        url = reverse('picture-list')
        self.assertEqual(resolve(url).func.view_class, PictureList)

    def test_pictures_shared_url(self):
        url = reverse('shared-picture-list')
        self.assertEqual(resolve(url).func.view_class, TimePictureList)

    def test_token_url(self):
        url = reverse('token-obtain-pair')
        self.assertEqual(resolve(url).func.view_class, TokenObtainPairView)

    def test_token_refresh_url(self):
        url = reverse('token-refresh')
        self.assertEqual(resolve(url).func.view_class, TokenRefreshView)

    def test_picture_details(self):
        url = reverse('picture-details', kwargs={'pk': "3574baa7-e238-484e-8691-8d1c2287e06e"})
        url_height = reverse('picture-details', kwargs={'pk': "3574baa7-e238-484e-8691-8d1c2287e06e", 'height': 200})
        self.assertEqual(resolve(url).func.view_class, PictureDetails)
        self.assertEqual(resolve(url_height).func.view_class, PictureDetails)

    def test_picture_time_link_details(self):
        url = reverse('picture-time-link', kwargs={'pk': "3574baa7-e238-484e-8691-8d1c2287e06e"})
        self.assertEqual(resolve(url).func.view_class, TimePictureDetails)


class PictureListTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='admin')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.url = reverse('picture-list')

    def test_method_get_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data,
                         PictureSerializer(Picture.objects.filter(owner__user=self.user), many=True).data)

    def test_method_get_unauthenticated(self):
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_method_post_authenticated_valid(self):
        img = SimpleUploadedFile(name='test_image.png', content=open("media/test_image.png", 'rb').read(),
                                 content_type='image/png')
        data = {
            'name': "test",
            'img': img
        }
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(True, Picture.objects.filter(owner__user=self.user, name="test").exists())

    def test_method_post_authenticated_invalid(self):
        data = {
            'name': "test",
            'img': "test_image.png"
        }
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(False, Picture.objects.filter(owner__user=self.user).exists())


class TimePictureListTest(APITestCase):
    url = reverse('shared-picture-list')

    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='admin')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.picture = Picture.objects.create(owner=Account.objects.get(user=self.user), img="imgmock.png")
        TimeExpiringPicture.objects.create(picture=self.picture, time=400)

    def test_method_get_authorized(self):
        response = self.client.get(self.url)
        query = TimeExpiringPicture.objects.filter(picture__owner=Account.objects.get(user=self.user))
        serializer = TimePictureSerializer(query, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_method_get_unauthenticated(self):
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.url)
        data = {
            "detail": "Authentication credentials were not provided."
        }
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, data)


class PictureDetailsTests(APITestCase):

    def setUp(self):
        user = User.objects.create_user(username='admin', password='admin')
        self.account = Account.objects.get(user=user)
        self.account.tier = Tier.objects.get(name="Premium")
        self.account.save()
        self.picture = Picture.objects.create(owner=self.account, img="image.jpg")
        self.picture.img = SimpleUploadedFile(name='test_image.jpg', content=open("media/test_image.png", 'rb').read(),
                                              content_type='image/jpeg')
        self.picture.save()
        self.uuid = self.picture.id
        self.token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.url = reverse('picture-details', kwargs={'pk': self.uuid})
        self.url_height = reverse('picture-details', kwargs={'pk': self.uuid, 'height': 200})

    def test_method_post_authenticated_valid(self):
        data = {
            'time': 800
        }
        response = self.client.post(self.url, data, format='json')
        object = TimeExpiringPicture.objects.filter(time=800, picture=self.picture).first()
        serializer = TimePictureSerializer(object)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data)

    def test_method_post_authenticated_invalid(self):
        data = {
            'time': 1
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(False, TimeExpiringPicture.objects.filter(time=1).exists())
        self.assertFalse(TimeExpiringPicture.objects.filter(time=1, picture=self.picture).exists(), False)

    def test_method_post_unauthenticated(self):
        self.client.force_authenticate(user=None, token=None)
        data = {
            'time': 800
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(False, TimeExpiringPicture.objects.filter(time=800).exists())

    def test_method_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_method_get_fake_uuid(self):
        response = self.client.get(reverse('picture-details', kwargs={'pk': '76807036-29ff-4f3a-a336-42bf2168ab27'}))
        response_height = self.client.get(
            reverse('picture-details', kwargs={'pk': '76807036-29ff-4f3a-a336-42bf2168ab27', 'height': 200}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_height.status_code, status.HTTP_404_NOT_FOUND)

    def test_method_get_correct_height(self):
        response = self.client.get(reverse('picture-details', kwargs={'pk': self.uuid, 'height': 200}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(reverse('picture-details', kwargs={'pk': self.uuid, 'height': 400}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_method_get_forbidden_height(self):
        response = self.client.get(reverse('picture-details', kwargs={'pk': self.uuid, 'height': 1000}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TimePictureDetailsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='admin')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        picture = Picture.objects.create(owner=Account.objects.get(user=self.user), img="imgmock.png")
        picture.img = SimpleUploadedFile(name='test_image.jpg', content=open("media/test_image.png", 'rb').read(),
                                         content_type='image/jpeg')
        picture.save()
        self.picture_good = TimeExpiringPicture.objects.create(picture=picture, time=400)
        self.picture_bad = TimeExpiringPicture.objects.create(picture=picture, time=0)

    def test_method_get_active(self):
        response = self.client.get(reverse('picture-time-link', kwargs={'pk': self.picture_good.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_method_get_expired(self):
        response = self.client.get(reverse('picture-time-link', kwargs={'pk': self.picture_bad.id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
