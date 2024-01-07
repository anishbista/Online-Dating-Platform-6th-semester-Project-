from django.db import models
from django.db.models import Q

from common.models import CommonInfo
from django.contrib.auth import get_user_model

User = get_user_model()


class PrivateChatThreadQuerySet(models.QuerySet):
    def get_private_chat_thread(self, user_1, user_2):
        qs = PrivateChatThread.objects.filter(
            Q(user_1=user_1, user_2=user_2) | Q(user_1=user_2, user_2=user_1)
        ).first()
        return qs


class PrivateChatThread(CommonInfo):
    user_1 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="first_user_chat_thread"
    )
    user_2 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="second_user_chat_thread"
    )

    objects = PrivateChatThreadQuerySet.as_manager()


class PrivateChatMessageQueryset(models.QuerySet):
    def get_all_messages(self, chat_thread):
        qs = PrivateChatMessage.objects.filter(chat_thread=chat_thread)
        return qs


class PrivateChatMessage(CommonInfo):
    chat_thread = models.ForeignKey(
        PrivateChatThread, on_delete=models.CASCADE, related_name="private_messages"
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    message_content = models.TextField(unique=False, blank=False, null=True)
    message_type = models.CharField(max_length=50, null=True, blank=True)
    is_read = models.BooleanField(default=False)

    objects = PrivateChatMessageQueryset.as_manager()

    def __str__(self) -> str:
        return self.sender.email
