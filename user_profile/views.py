from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse_lazy
from django.views.generic import UpdateView, ListView, DetailView, CreateView
from DatingAppProject.diffie_hellman import DiffieHellman
from user_profile.models import (
    UserConnection,
    UserDescription,
    UserProfile,
    Heart,
    UserInterest,
    Key,
)
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from DatingAppProject.decorators import profile_update_required
from notifications.signals import notify

decorators = [login_required, profile_update_required]


@login_required
@profile_update_required
def index(request):
    if request.user.profile.description.looking_for == "BOTH":
        userprofile_list = UserProfile.objects.exclude(user=request.user).order_by(
            "-created_on"
        )
    else:
        userprofile_list = (
            UserProfile.objects.filter(
                gender=request.user.profile.description.looking_for
            )
            .exclude(user=request.user)
            .order_by("-created_on")
        )
    userprofiles = [
        x
        for x in userprofile_list
        if x not in request.user.profile.blocked_users.users.all()
    ]
    return render(request, "index.html", {"userprofile_list": userprofiles})


@method_decorator(login_required, name="dispatch")
class UpdateProfile(UpdateView):
    model = UserProfile
    template_name = "profile/update_profile.html"
    success_url = reverse_lazy("index")
    fields = [
        "first_name",
        "last_name",
        "bio",
        "date_of_birth",
        "address",
        "phone",
        "gender",
        "profile_picture",
    ]


@login_required
def rightSwipeUser(request):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if is_ajax:
        if request.method == "POST":
            receiver_id = request.POST.get("receiver")
            receiver = UserProfile.objects.filter(id=receiver_id).first()
            data = {}
            if receiver == request.user.profile:
                data["message"] = "You cannot sent heart to yourself."
                data["status"] = "error"
                return JsonResponse(data)
            elif Heart.objects.filter(
                sent_by=request.user.profile, received_by=receiver
            ):
                if receiver in request.user.profile.connection.connections.all():
                    data["message"] = "Already in your connection list."
                    data["status"] = "error"
                else:
                    data["message"] = "Not responded to previous heart sent."
                    data["status"] = "error"
                return JsonResponse(data)
            else:
                Heart.objects.create(
                    sent_by=request.user.profile,
                    received_by=receiver,
                )
                data["message"] = "Heart successfully sent."
                data["status"] = "success"
                if (
                    Heart.objects.get_mutual_hearts(
                        request.user.profile, receiver
                    ).count()
                    >= 2
                ):
                    request.user.profile.connection.connections.add(receiver)
                    receiver.connection.connections.add(request.user.profile)
            notify.send(request.user, recipient=receiver.user, verb="Sent you a heart.")
            return JsonResponse(data)
        else:
            return JsonResponse({"status": "Invalid Request"}, status=400)
    else:
        return HttpResponseBadRequest("Invalid Request.")


@login_required
@profile_update_required
def list_user_notifications(request):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if is_ajax:
        notifications = request.user.notifications.all()
        context = {
            "notifications": notifications,
        }
        return render(request, "profile/list_notifications.html", context)
    else:
        if request.method == "GET":
            notifications = request.user.notifications.all()
            context = {
                "notifications": notifications,
                "title": "Notifications",
            }
            return render(request, "profile/base_notifications.html", context)


class UserDetailView(DetailView):
    model = UserProfile
    template_name = "profile/user_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hearts_received"] = Heart.objects.filter(
            received_by=self.kwargs.get("pk")
        )
        context["hearts_sent"] = Heart.objects.filter(sent_by=self.kwargs.get("pk"))
        context["interests"] = UserInterest.objects.filter(user=self.kwargs.get("pk"))
        context["title"] = "Profile"
        return context


class AddUserInterest(CreateView):
    model = UserInterest
    fields = ["title"]
    template_name = "profile/user_detail.html"

    def get_success_url(self):
        pk = self.request.user.profile.id
        return reverse_lazy("profile_detail", kwargs={"pk": pk})

    def form_valid(self, form):
        form.instance.user = self.request.user.profile
        return super().form_valid(form)


class UpdateUserDescription(UpdateView):
    model = UserDescription
    fields = [
        "height",
        "eye_color",
        "hair_length",
        "hair_colour",
        "body_type",
        "religion",
        "relationship_status",
        "education",
        "looking_for",
    ]
    template_name = "profile/update_user_description.html"

    def get_success_url(self):
        pk = self.request.user.profile.id
        return reverse_lazy("profile_detail", kwargs={"pk": pk})


@login_required
def testing(request):
    user_1_public_key = request.user.keys.public_key
    user_2_keys = Key.objects.exclude(keys_owner=request.user).first()
    user_2_shared_key = DiffieHellman.generate_shared_key_static(
        user_2_keys.private_key, user_1_public_key
    )
    user_1_shared_key = DiffieHellman.generate_shared_key_static(
        request.user.keys.private_key, user_2_keys.public_key
    )
    context = {
        "user_1_private_key": request.user.keys.private_key,
        "user_1_public_key": user_1_public_key,
        "user_2_keys": user_2_keys,
        "user_2_shared_key": user_2_shared_key,
        "user_1_shared_key": user_1_shared_key,
    }
    return render(request, "testing.html", context)
