from django.urls import path
from chat.views import (
    ChatBoxView,
    get_private_chat,
    get_shared_key,
    delete_chat_thread,
    block_user,
)

urlpatterns = [
    path("", ChatBoxView, name="chatbox"),
    path("get_messages/", get_private_chat, name="get_private_chat"),
    path("get_shared_key/", get_shared_key, name="get_shared_key"),
    path("delete_chat/", delete_chat_thread, name="delete-chat"),
    path("block_user/", block_user),
]
