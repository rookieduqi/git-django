# myapp/models.py
from django.db import models


class RepositoryGroup(models.Model):
    name = models.CharField(max_length=255, unique=True)
    remark = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class GroupMember(models.Model):
    group_id = models.IntegerField()  # 逻辑外键
    username = models.CharField(max_length=255)

    def __str__(self):
        return self.username


class Repository(models.Model):
    name = models.CharField(max_length=100)
    remark = models.TextField(blank=True, null=True)
    group_id = models.IntegerField()
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)


class RepositoryMember(models.Model):
    repository_id = models.IntegerField()
    username = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
