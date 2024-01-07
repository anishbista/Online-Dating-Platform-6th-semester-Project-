from django import template
import geopy.distance

from accounts.models import User
from user_profile.models import UserProfile

register = template.Library()


@register.simple_tag
def calculate_distance(user_id, pk):
    request_user = User.objects.filter(id=user_id).first()
    coords_1 = (request_user.profile.long, request_user.profile.lat)
    user_obj = UserProfile.objects.filter(id=pk).first()
    coords_2 = (user_obj.long, user_obj.lat)
    return int(geopy.distance.geodesic(coords_1, coords_2).km)
