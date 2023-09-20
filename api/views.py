from PIL import Image
from django.http import Http404, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from core.models import *
from api.serializers import *


class PictureList(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Picture.objects.filter(owner__user=self.request.user)

    def perform_create(self, serializer):
        account=Account.objects.get(user=self.request.user)
        serializer.save(owner=account)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PictureAddSerializer
        if self.request.method == "GET":
            return PictureSerializer


class PictureDetails(APIView):

    def get_permissions(self):
        return [permissions.IsAuthenticatedOrReadOnly()]

    def get_object(self, pk):
        try:
            return Picture.objects.get(pk=pk)
        except Picture.DoesNotExist:
            raise Http404

    def get_post_object(self, pk):
        try:
            user = Account.objects.get(user=self.request.user)
            return Picture.objects.get(pk=pk, owner=user)
        except Picture.DoesNotExist:
            raise Http404

    def get(self, request, pk, height=None):
        # returns image in given size
        picture = self.get_object(pk)
        if height:
            try:
                height_model = FileHeight.objects.get(size=height)
            except FileHeight.DoesNotExist:
                raise PermissionDenied({"message": "Specified file height not found!",
                                        "object": picture})
            if picture.owner.tier.sizes_allowed.contains(height_model):
                image = Image.open(picture.img)
                image.thumbnail((image.width, height), Image.LANCZOS)
                response = HttpResponse(content_type='image/jpg')
                if image.mode in ("RGBA", "P"):
                    image = image.convert("RGB")
                image.save(response, "JPEG")
                return response
            else:
                raise PermissionDenied({"message": "This picture cannot be displayed at this height",
                                        "object": picture})
        else:
            if picture.owner.tier.allow_original:
                return HttpResponse(picture.img, content_type="image/png")
            else:
                raise PermissionDenied({"message": "This picture cannot be displayed in its full resolution",
                                        "object": picture})

    def post(self, request, pk):
        picture = self.get_post_object(pk)
        serializer = TimePictureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(picture=picture)
            return Response(serializer.data, status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TimePictureList(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TimePictureSerializer

    def get_queryset(self):
        pictures = TimeExpiringPicture.objects.filter(picture__owner__user=self.request.user, expires__gt=timezone.now())
        return pictures


class TimePictureDetails(APIView):
    def get_object(self, pk):
        try:
            return TimeExpiringPicture.objects.get(pk=pk, expires__gt=timezone.now())
        except TimeExpiringPicture.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        time_picture = self.get_object(pk)
        return HttpResponse(time_picture.picture.img, content_type="image/png")

# TODO cache
