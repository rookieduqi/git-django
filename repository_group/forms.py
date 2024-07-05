# user/forms.py

from django import forms
from .models import RepositoryGroup


class RepositoryGroupForm(forms.ModelForm):
    class Meta:
        model = RepositoryGroup
        fields = ['name', 'remark']


