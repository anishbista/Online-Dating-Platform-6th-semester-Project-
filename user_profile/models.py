from datetime import date
import os
from pyexpat import model
import uuid

import math
from django.db.models.expressions import RawSQL
from django.db.backends.signals import connection_created
from django.dispatch import receiver

from bisect import bisect
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from common.constants import (
    HEIGHT,
    LOOKING_FOR_CHOICES,
    GENDER_CHOICES,
    signs,
    ZODIAC_CHOICES,
    HAIR_COLOUR,
    HAIR_LENGTH,
    BODY_TYPE,
    RELIGION,
    RELATIONSHIP_STATUS,
    EDUCATION,
    EYE_COLOR,
    HEIGHT,
)
from common.models import CommonInfo


User = settings.AUTH_USER_MODEL


def validate_age(value):
    if value and (timezone.now().date() - value).days < 365.25 * 18:
        raise ValidationError("User must be 18 years or older.")


def validate_phone_number(value):
    if not value.isdigit() or len(value) != 10:
        raise ValidationError(
            _("Phone number must contain exactly 10 digits."),
            code="invalid_phone_number",
        )


# Renames user uploaded images
def path_and_rename(instance, filename):
    upload_to = "media/profile_images"
    ext = filename.split(".")[-1]

    if instance.pk:
        filename = "{}.{}".format(instance.pk, ext)
    else:
        filename = "{}.{}".format(uuid.uuid4().hex, ext)
    return os.path.join(upload_to, filename)


# Profile model for user-- contains personal information
class UserProfile(CommonInfo):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    bio = models.TextField(max_length=100, default="", blank=False)
    date_of_birth = models.DateField(null=True, validators=[validate_age])
    address = models.CharField(max_length=100, null=True)
    phone = models.CharField(
        max_length=10, null=True, validators=[validate_phone_number]
    )

    gender = models.CharField(choices=GENDER_CHOICES, max_length=6, default="MALE")

    profile_picture = models.ImageField(upload_to=path_and_rename, null=True)

    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    long = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    age = models.IntegerField(null=True, blank=True)
    zodiac = models.CharField(
        choices=ZODIAC_CHOICES, max_length=15, null=True, blank=True
    )

    def save(self, *args, **kwargs):
        if self.date_of_birth is not None:
            self.age = self.get_age()
            self.zodiac = self.get_zodiac()
        super(UserProfile, self).save(*args, **kwargs)

    def get_age(self):
        return int((date.today() - self.date_of_birth).days / 365.25)

    def get_zodiac(self):
        month = int(self.date_of_birth.strftime("%m"))
        day = int(self.date_of_birth.strftime("%d"))
        return signs[bisect(signs, (month, day))][2]

    def __str__(self):
        return self.user.email


class UserDescription(CommonInfo):
    user = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, related_name="description"
    )
    height = models.CharField(choices=HEIGHT, default="4 to 5", max_length=10)
    eye_color = models.CharField(choices=EYE_COLOR, max_length=10, default="BLACK")
    hair_length = models.CharField(
        choices=HAIR_LENGTH, default="LONG", blank=False, max_length=100
    )
    hair_colour = models.CharField(
        choices=HAIR_COLOUR, default="BLACK", blank=False, max_length=10
    )
    body_type = models.CharField(
        choices=BODY_TYPE, default="AVERAGE", blank=False, max_length=15
    )
    religion = models.CharField(
        choices=RELIGION, default="HINDU", blank=False, max_length=100
    )
    relationship_status = models.CharField(
        choices=RELATIONSHIP_STATUS, default="SINGLE", blank=False, max_length=100
    )
    education = models.CharField(
        choices=EDUCATION, default="HIGH SCHOOL", blank=False, max_length=100
    )
    looking_for = models.CharField(
        choices=LOOKING_FOR_CHOICES, max_length=6, default="BOTH"
    )
    is_completed = models.BooleanField(default=False)


class UserInterest(CommonInfo):
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="interest"
    )
    title = models.CharField(max_length=20, blank=True, null=True)


class UserConnection(CommonInfo):
    owner = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, related_name="connection"
    )
    connections = models.ManyToManyField(UserProfile)

    def __str__(self):
        return self.owner.user.email


class BlockedUser(CommonInfo):
    owner = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, related_name="blocked_users"
    )
    users = models.ManyToManyField(UserProfile)

    def __str__(self):
        return self.owner.user.email


class HeartQuerySet(models.QuerySet):
    def get_mutual_hearts(self, user_1, user_2):
        qs = Heart.objects.filter(
            Q(sent_by=user_1, received_by=user_2)
            | Q(sent_by=user_2, received_by=user_1)
        )
        return qs


class Heart(CommonInfo):
    sent_by = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="heart_sender"
    )
    received_by = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="heart_receiver"
    )

    objects = HeartQuerySet.as_manager()


class Key(models.Model):
    keys_owner = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="keys"
    )
    private_key = models.TextField(blank=True, null=True)
    public_key = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.keys_owner.email
