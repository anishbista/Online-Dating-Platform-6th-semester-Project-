from turtle import title
from django.contrib import admin
from user_profile.models import (
    UserProfile,
    Heart,
    UserDescription,
    UserInterest,
    UserConnection,
    Key,
    BlockedUser,
)


@admin.register(Heart)
class HeartAdmin(admin.ModelAdmin):
    list_display = ["sent_by", "received_by", "created_on"]


@admin.register(UserDescription)
class UserDescriprionAdmin(admin.ModelAdmin):
    list_display = ["user"]


@admin.register(UserInterest)
class UserInterestAdmin(admin.ModelAdmin):
    list_display = ["user", "title"]


admin.site.register(Key)
admin.site.register(UserProfile)
admin.site.register(UserConnection)
admin.site.register(BlockedUser)
