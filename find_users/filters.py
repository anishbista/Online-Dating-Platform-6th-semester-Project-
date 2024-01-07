import django_filters
from user_profile.models import UserDescription, UserProfile


class UserFilter(django_filters.FilterSet):
    address = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = UserProfile
        fields = [
            "gender",
            "age",
            "zodiac",
            "address",
            "description__height",
            "description__eye_color",
            "description__hair_length",
            "description__hair_colour",
            "description__body_type",
            "description__religion",
            "description__relationship_status",
            "description__education",
            "interest__title",
        ]
