from django import forms
from django.contrib.auth.forms import UserCreationForm


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)
