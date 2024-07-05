# serializers.py
from rest_framework import serializers
from .models import RepositoryGroup, GroupMember, Repository, RepositoryMember


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
        fields = '__all__'
