from django import forms
from user_profile.models import UserDescription


class UserDescriptionForm(forms.ModelForm):
    class Meta:
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
        ]
