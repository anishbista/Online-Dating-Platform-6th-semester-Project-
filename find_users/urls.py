from django.urls import path
from find_users.views import FilterUser, get_users_by_raduis


urlpatterns = [
    path("users/", FilterUser, name="filter_user"),
    path("by_radius/", get_users_by_raduis),
]
