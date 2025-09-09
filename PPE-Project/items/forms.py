# items/forms.py
from django import forms
from django.forms.widgets import DateTimeInput
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Order, PickupHub


class SignupForm(UserCreationForm):
    """
    Require email at signup so logged-in users always have an email on file.
    """
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'customer_name',
            'customer_email',
            'customer_address',
            'quantity',
            'pickup_hub',
            'pickup_datetime',
        ]
        widgets = {
            'pickup_datetime': DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # For authenticated users, hide name/email (we’ll fill from user account in the view)
        if user and user.is_authenticated:
            self.fields['customer_name'].required = False
            self.fields['customer_email'].required = False
            self.fields['customer_name'].widget = forms.HiddenInput()
            self.fields['customer_email'].widget = forms.HiddenInput()
