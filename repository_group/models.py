# myapp/models.py
from django.db import models


class RepositoryGroup(models.Model):
    name = models.CharField(max_length=255, unique=True)
    remark = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'repository_group'


class GroupMember(models.Model):
    group_id = models.IntegerField()  # 逻辑外键
    username = models.CharField(max_length=255)

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'group_member'


class Repository(models.Model):
    name = models.CharField(max_length=100)
    remark = models.TextField(blank=True, null=True)
    group_id = models.IntegerField()
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'repository'
        # unique_together = ('name', 'group_id')  # 添加唯一约束


class Role(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    remark = models.TextField()

    class Meta:
        db_table = 'role'


# class RepositoryMember(models.Model):
#     id = models.AutoField(primary_key=True)
#     repository_id = models.IntegerField()
#     user_id = models.IntegerField()
#     role_id = models.IntegerField()

class RepositoryMember(models.Model):
    username = models.CharField(max_length=255)
    repository_id = models.IntegerField()
    role_id = models.IntegerField()

    @property
    def role_name(self):
        role = Role.objects.get(id=self.role_id)
        return role.name

    class Meta:
        db_table = 'repository_member'


class Branch(models.Model):
    name = models.CharField(max_length=100)
    sync_branch = models.CharField(max_length=100)
    remark = models.TextField(null=True, blank=True)
    repository_group_id = models.IntegerField()
    repository_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'repository_branch'
        # unique_together = ('name', 'repository_id')


class BranchMember(models.Model):
    branch_id = models.IntegerField()
    username = models.CharField(max_length=100)
    role_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def role_name(self):
        role = Role.objects.get(id=self.role_id)
        return role.name

    class Meta:
        db_table = 'branch_member'


class Hook(models.Model):
    repository_group_id = models.IntegerField()
    repository_id = models.IntegerField()
    branch_name = models.CharField(max_length=100)
    hook_url = models.URLField()
    remark = models.TextField(null=True, blank=True)
    trigger_event = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'branch_hook'


class ImportedRepository(models.Model):
    url = models.URLField()
    authenticated = models.BooleanField(default=False)
    username = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'import_repository'


# class WebhookTriggerRecord(models.Model):
#     hook_url = models.URLField()
#     status = models.CharField(max_length=10)  # "成功" 或 "失败"
#     trigger_time = models.DateTimeField(auto_now_add=True)
#     response_content = models.TextField()
#
#     class Meta:
#         db_table = 'web_hook_trigger_record'

class WebhookTriggerRecord(models.Model):
    hook_url = models.URLField()
    event = models.CharField(max_length=50)  # 新增事件类型字段
    branch = models.CharField(max_length=100)  # 新增分支字段
    status = models.CharField(max_length=10)  # "成功" 或 "失败"
    trigger_time = models.DateTimeField(auto_now_add=True)
    response_content = models.TextField()

    class Meta:
        db_table = 'web_hook_trigger_record'
