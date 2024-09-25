from django.shortcuts import render
from django.http import HttpResponseBadRequest, JsonResponse
from user_profile.models import BlockedUser, UserProfile, Heart
from find_users.filters import UserFilter
from .utilities import calculate_distance
from django.db.models import Exists
from django.template.loader import render_to_string


def FilterUser(request):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if is_ajax:
        blocked_users = [x.user for x in request.user.profile.blocked_users.users.all()]
        liked_profiles_ids = Heart.objects.filter(
            sent_by=request.user.profile
        ).values_list("received_by__id", flat=True)

        if request.method == "POST":
            f = UserFilter(
                request.POST,
                queryset=UserProfile.objects.exclude(user=request.user)
                .exclude(user__in=blocked_users)
                .exclude(id__in=liked_profiles_ids)  # Exclude liked profiles
                .order_by("-created_on"),
            )
            return render(request, "filter_users_list.html", {"filter": f})
        else:
            return JsonResponse({"status": "Invalid Request"}, status=400)
    else:
        blocked_users = [x.user for x in request.user.profile.blocked_users.users.all()]
        liked_profiles_ids = Heart.objects.filter(
            sent_by=request.user.profile
        ).values_list("received_by__id", flat=True)

        f = UserFilter(
            request.GET,
            queryset=UserProfile.objects.exclude(user=request.user)
            .exclude(user__in=blocked_users)
            .exclude(id__in=liked_profiles_ids)  # Exclude liked profiles
            .order_by("-created_on"),
        )
        return render(request, "filter_users.html", {"filter": f, "title": "Filter"})


def get_users_by_raduis(request):
    if request.method == "GET":
        range = request.GET.get("range", 10)  # Default to 10 km
        range = int(range)

        # Get the list of users filtered by distance and looking for gender
        querylist = [
            x
            for x in UserProfile.objects.exclude(user=request.user)
            if calculate_distance(request.user, x.lat, x.long) <= range
            and (
                request.user.profile.description.looking_for == "BOTH"
                or x.gender == request.user.profile.description.looking_for
            )
        ]

        return render(
            request, "user_list_partial.html", {"userprofile_list": querylist}
        )

    return JsonResponse({"status": "Invalid Request"}, status=400)
