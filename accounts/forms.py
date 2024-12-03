from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    balance = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        initial=0.0,
        help_text="Optional starting balance",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("email", "balance")
