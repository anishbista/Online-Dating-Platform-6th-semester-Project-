import email
import json
from time import timezone
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from DatingAppProject.diffie_hellman import DiffieHellman
from DatingAppProject.xor import decrypt_message
from chat.models import PrivateChatThread, PrivateChatMessage
from user_profile.models import Key


User = get_user_model()


def get_public_key(target_user):
    qs = Key.objects.filter(keys_owner=target_user).first()
    return qs.public_key


def get_private_key(user):
    qs = Key.objects.filter(keys_owner=user).first()
    return qs.private_key


class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_1 = self.scope["user"]
        self.user_2 = self.scope["url_route"]["kwargs"]["userId"]
        self.public_key = await sync_to_async(get_public_key)(self.user_2)
        self.chat_thread = await sync_to_async(
            PrivateChatThread.objects.get_private_chat_thread
        )(
            self.user_1,
            self.user_2,
        )

        self.other_user_room_group_name = "chat_%s" % self.user_2
        self.room_group_name = "chat_%s" % self.user_1.id

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()

        await self.send(
            text_data=json.dumps(
                {"p_key": self.public_key},
            )
        )

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        type = text_data_json["type"]
        command = text_data_json.get("command")
        message = text_data_json.get("message")
        sent_by = text_data_json["sent_by"]
        sent_to = text_data_json["sent_to"]

        self.sender = await sync_to_async(User.get_user.by_email)(email=self.user_1)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": type,
                "command": command,
                "message": message,
                "sent_by": sent_by,
                "sent_to": sent_to,
                "chat_thread_id": self.chat_thread.id,
            },
        )

        if command == "private_chat":
            local_private_key = await sync_to_async(get_private_key)(self.user_1)
            local_shared_key = await sync_to_async(
                DiffieHellman.generate_shared_key_static
            )(local_private_key, self.public_key)
            # decrypted_msg = decrypt_message(message, local_shared_key)

            await sync_to_async(PrivateChatMessage.objects.create)(
                chat_thread=self.chat_thread,
                sender=self.sender,
                message_content=message,
                message_type=type,
            )

        await self.channel_layer.group_send(
            self.other_user_room_group_name,
            {
                "type": type,
                "command": command,
                "message": message,
                "sent_by": sent_by,
                "sent_to": sent_to,
                "chat_thread_id": self.chat_thread.id,
            },
        )

    # Receive message from room group
    async def chat_message(self, event):
        type = event["type"]
        command = event["command"]
        message = event["message"]
        sent_by = event["sent_by"]
        sent_to = event["sent_to"]
        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "type": type,
                    "command": command,
                    "message": message,
                    "sent_by": sent_by,
                    "sent_to": sent_to,
                    "timestamp": timezone.localtime(timezone.now()).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                },
                cls=DjangoJSONEncoder,
            )
        )
