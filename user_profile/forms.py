from django import forms
from user_profile.models import UserProfile


class UserFilterForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "gender",
            "age",
            "zodiac",
        ]
