from django.urls import re_path
from chat.consumers import PrivateChatConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<userId>[0-9A-Fa-f-]+\w+)/$", PrivateChatConsumer.as_asgi()),
]
