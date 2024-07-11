# serializers.py
from rest_framework import serializers
from .models import RepositoryGroup, GroupMember, Repository, RepositoryMember, Role, Branch, BranchMember, Hook, \
    ImportedRepository, WebhookTriggerRecord
from user.models import CustomUser


class RepositoryGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryGroup
        fields = '__all__'


class GroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMember
        fields = '__all__'


class RepositorySerializer(serializers.ModelSerializer):
    group_name = serializers.SerializerMethodField()

    class Meta:
        model = Repository
        fields = '__all__'

    def get_group_name(self, obj):
        try:
            group = RepositoryGroup.objects.get(id=obj.group_id)
            return group.name
        except RepositoryGroup.DoesNotExist:
            return None


# class RepositorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Repository
#         fields = '__all__'

class RepositoryMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryMember
        fields = ['id', 'username', 'repository_id', 'role_id', 'role_name']
        # fields = '__all__'

    def get_role_name(self, obj):
        try:
            role = Role.objects.get(id=obj.role_id)
            return role.name
        except Role.DoesNotExist:
            return None


class BranchSerializer(serializers.ModelSerializer):
    repository_name = serializers.SerializerMethodField()
    repository_group_name = serializers.SerializerMethodField()

    class Meta:
        model = Branch
        # fields = ['id', 'name', 'repository_id', 'sync_branch', 'repository_name', 'created_at', 'remark']
        fields = '__all__'

    def get_repository_name(self, obj):
        try:
            repository = Repository.objects.get(id=obj.repository_id)
            return repository.name
        except Repository.DoesNotExist:
            return None

    def get_repository_group_name(self, obj):
        try:
            repository_group = RepositoryGroup.objects.get(id=obj.repository_group_id)
            return repository_group.name
        except RepositoryGroup.DoesNotExist:
            return None


class BranchMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = BranchMember
        fields = ['id', 'username', 'branch_id', 'role_id', 'role_name']
        # fields = '__all__'

    def get_role_name(self, obj):
        try:
            role = Role.objects.get(id=obj.role_id)
            return role.name
        except Role.DoesNotExist:
            return None


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'


class HookSerializer(serializers.ModelSerializer):
    repository_group_name = serializers.SerializerMethodField()
    repository_name = serializers.SerializerMethodField()

    class Meta:
        model = Hook
        fields = '__all__'

    def get_repository_group_name(self, obj):
        try:
            repository_group = RepositoryGroup.objects.get(id=obj.repository_group_id)
            return repository_group.name
        except RepositoryGroup.DoesNotExist:
            return None

    def get_repository_name(self, obj):
        try:
            repository = Repository.objects.get(id=obj.repository_id)
            return repository.name
        except Repository.DoesNotExist:
            return None


class ImportRepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportedRepository
        fields = '__all__'


class WebhookTriggerRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookTriggerRecord
        fields = '__all__'

    # def create(self, validated_data):
    #     # 使用 get 方法获取参数，如果参数不存在，则设置为空或默认值
    #     hook_url = validated_data.get('hook_url', '')
    #     event = validated_data.get('event', '')
    #     branch = validated_data.get('branch', '')
    #     status = validated_data.get('status', '')
    #     response_content = validated_data.get('response_content', '')
    #
    #     # 创建新的 WebhookTriggerRecord 实例
    #     return WebhookTriggerRecord.objects.create(
    #         hook_url=hook_url,
    #         event=event,
    #         branch=branch,
    #         status=status,
    #         response_content=response_content
    #     )
