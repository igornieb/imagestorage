import uuid
from datetime import timedelta
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


class FileHeight(models.Model):
    def __str__(self):
        return f"{self.size}"

    size = models.PositiveIntegerField(unique=True)


class Tier(models.Model):
    def __str__(self):
        return f"{self.name}, {self.sizes_allowed}"

    name = models.CharField(max_length=100, unique=True)
    sizes_allowed = models.ManyToManyField(FileHeight)
    allow_original = models.BooleanField(default=False)
    allow_link = models.BooleanField(default=False)


class Account(models.Model):
    # TODO extend base user

    def __str__(self):
        return f"{self.username} - {self.tier}"

    tier = models.ForeignKey(Tier, on_delete=models.CASCADE)


class Picture(models.Model):
    def __str__(self):
        return f"{self.name} - {self.owner}"

    def upload_to(self, filename):
        return f"user-pictures/{self.owner.username}/{filename}"

    def get_absolute_url(self):
        # get posible res, create urls
        heights = self.owner.tier.sizes_allowed.all()
        links = []
        for value in heights:
            links.append(reverse("picture-details", kwargs={'pk': self.pk, "height": value.size}))
        if self.owner.tier.allow_original:
            links.append(reverse("picture-details", kwargs={'pk': self.pk}))
        return links

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(Account, on_delete=models.CASCADE)
    img = models.ImageField(upload_to=upload_to, null=False, blank=False,
                            validators=[FileExtensionValidator((['jpg', 'png']))])


class TimeExpiringPicture(models.Model):
    def __str__(self):
        return f"{self.picture} {self.created} {self.expires}"

    def get_absolute_url(self):
        return reverse("timelink", kwargs={'pk': self.pk})

    def time_left(self):
        time_left = (self.expires - timezone.now()).total_seconds()
        if time_left < 0:
            return "Expired"
        return round(time_left)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    picture = models.ForeignKey(Picture, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    time = models.IntegerField(null=False, validators=[validate_time_allowed])
    expires = models.DateTimeField(default=timezone.now, null=True)

    def save(self, *args, **kwargs):
        self.expires = self.created + timedelta(seconds=self.time)
        super(TimeExpiringPicture, self).save(*args, **kwargs)
