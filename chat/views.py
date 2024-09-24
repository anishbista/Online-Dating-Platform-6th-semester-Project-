import json
from django.shortcuts import render
from django.http import HttpResponseBadRequest, JsonResponse
from chat.models import PrivateChatThread, PrivateChatMessage
from user_profile.models import UserConnection, Key, BlockedUser, UserProfile
from DatingAppProject.diffie_hellman import DiffieHellman
from django.contrib.auth import get_user_model
from DatingAppProject.aes_des import encrypt_message, decrypt_message
from DatingAppProject.xor import decrypt_message as dec2
from django.db.models import F


User = get_user_model()


def ChatBoxView(request):
    logged_in_user = User.objects.values("id", "email").get(id=request.user.id)

    connections = UserConnection.objects.filter(owner=request.user.profile).first()

    context = {
        "connections": connections,
        "logged_in_user": logged_in_user,
        "title": "Chat",
    }
    return render(request, "chatbox.html", context)


def get_private_chat(request):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if is_ajax:
        user_1 = request.user
        user_2 = request.GET.get("user_2", None)
        user_2_instance = User.objects.filter(id=user_2).first()
        private_chat_thread = PrivateChatThread.objects.get_private_chat_thread(
            user_1,
            user_2_instance,
        )
        if not private_chat_thread:
            private_chat_thread = PrivateChatThread.objects.create(
                user_1=user_1,
                user_2=user_2_instance,
            )
            private_chat_thread.save()
        local_shared_key = DiffieHellman.generate_shared_key_static(
            request.user.keys.private_key, user_2_instance.keys.public_key
        )
        messages = PrivateChatMessage.objects.get_all_messages(
            chat_thread=private_chat_thread
        )
        for message in messages:
            message.message_content = decrypt_message(
                message.message_content, local_shared_key
            )
            print("local_shared_key2", local_shared_key)

            print("mess2", message.message_content)
            message.message_content = dec2(message.message_content, local_shared_key)
            print("mess2", message.message_content)

        unread_messages = messages.filter(is_read=False, sender=user_2_instance)
        for message in unread_messages:
            if request.user != message.sender:
                message.is_read = True
                message.save()
        context = {
            "thread_messages": messages,
        }
        return render(request, "chat_messages.html", context)
    else:
        return HttpResponseBadRequest("Invalid request")


def get_shared_key(request):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if is_ajax:
        data = {}
        public_key = request.GET.get("p_key")
        user = request.user
        qs = Key.objects.filter(keys_owner=user).first()
        local_private_key = qs.private_key
        if qs.keys_owner != user:
            return JsonResponse({"status": "You are not Allowed"}, status=400)
        shared_key = DiffieHellman.generate_shared_key_static(
            local_private_key, public_key
        )
        data["s_key"] = shared_key
        return JsonResponse(data, status=200)
    else:
        return HttpResponseBadRequest("Invalid request")


def delete_chat_thread(request):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if is_ajax:
        if request.method == "DELETE":
            data = json.load(request)
            user_2 = data.get("connection")
            user_2_instance = User.objects.filter(id=user_2).first()
            private_chat_thread = PrivateChatThread.objects.get_private_chat_thread(
                request.user, user_2_instance
            )
            qs = PrivateChatMessage.objects.get_all_messages(private_chat_thread)
            qs.delete()
            return JsonResponse(
                {"status": "Conversation Deleted Successfully"}, status=200
            )
        else:
            return JsonResponse({"status:Invalid Request"}, status=400)
    else:
        return HttpResponseBadRequest("Invalid Request")


def block_user(request):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if is_ajax:
        if request.method == "POST":
            target_user_id = request.POST.get("target_user_id")
            target_user = User.objects.filter(id=target_user_id).first()
            if not BlockedUser.objects.filter(owner=request.user.profile):
                BlockedUser.objects.create(owner=request.user.profile)
            request.user.profile.blocked_users.users.add(target_user.profile)
            request.user.profile.connection.connections.remove(target_user.profile)
            target_user.profile.connection.connections.remove(request.user.profile)
            return JsonResponse(
                {"status": "Successfully blocked the user."}, status=200
            )
        else:
            return JsonResponse({"status": "Invalid Request"}, status=400)

    else:
        return HttpResponseBadRequest("Invalid Request")
