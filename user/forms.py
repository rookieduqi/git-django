# user/forms.py
from django import forms
from .models import CustomUser


class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'remark']


class CustomUserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['remark', 'is_disabled']


class PasswordResetForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['password']


class CustomUserPasswordResetForm(forms.ModelForm):
    new_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['new_password']



