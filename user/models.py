# user/models.py
from django.db import models


class CustomUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    remark = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_disabled = models.BooleanField(default=False)

    def __str__(self):
        return self.username

