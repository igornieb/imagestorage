from django.contrib import admin
from core.models import *


@admin.register(Tier)
class TierAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'tier',)


@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):
    list_display = ('pk', 'owner',)


@admin.register(TimeExpiringPicture)
class TimePictureAdmin(admin.ModelAdmin):
    list_display = ('pk', 'picture', 'expires')


@admin.register(FileHeight)
class FileHorizontalHeight(admin.ModelAdmin):
    list_display = ('size',)