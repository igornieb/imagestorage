from django.urls import path, include
from api.views import *

urlpatterns = [
    path('pictures', PictureList.as_view(), name='picture-list'),
]
