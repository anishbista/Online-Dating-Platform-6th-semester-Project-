from django.contrib import admin
from chat.models import PrivateChatThread, PrivateChatMessage


@admin.register(PrivateChatThread)
class PriavteChatAdmin(admin.ModelAdmin):
    list_display = ["user_1", "user_2"]


admin.site.register(PrivateChatMessage)
