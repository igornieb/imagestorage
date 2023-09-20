from django.urls import path, include
from api.views import *

urlpatterns = [
    path('pictures', PictureList.as_view(), name='picture-list'),
    path('pictures/shared', TimePictureList.as_view(), name='shared-picture-list'),
    path('picture/<uuid:pk>', PictureDetails.as_view(), name='picture-details'),
    path('picture/<uuid:pk>/<int:height>', PictureDetails.as_view(), name='picture-details'),
    path('picture-time-link/<uuid:pk>', TimePictureDetails.as_view(), name='picture-time-link'),
]
