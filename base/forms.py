from django import forms
from django.forms import ModelForm

from base.models import *


class UserSignUpForm(ModelForm):
    class Meta:
        model = User
        fields = [

        ]


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = [
            'business_name',
            'email',
            'phone_number'
        ]

