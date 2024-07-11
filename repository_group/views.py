from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from django.conf import settings
import json
import subprocess
import requests
from user.models import CustomUser

from .models import (
    RepositoryGroup,
    GroupMember,
    Repository,
    RepositoryMember,
    Role,
    Branch,
    BranchMember,
    Hook,
    ImportedRepository,
    WebhookTriggerRecord
)

from .serializers import (
    RepositoryGroupSerializer,
    GroupMemberSerializer,
    RepositorySerializer,
    RepositoryMemberSerializer,
    RoleSerializer,
    UserSerializer,
    BranchSerializer,
    BranchMemberSerializer,
    HookSerializer,
    ImportRepositorySerializer,
    WebhookTriggerRecordSerializer
)


class RepositoryGroupViewSet(viewsets.ModelViewSet):
    queryset = RepositoryGroup.objects.all()
    serializer_class = RepositoryGroupSerializer
    parser_classes = [JSONParser]

    def call_script(self, script_args):
        try:
            result = subprocess.run([settings.EDITOR_DIR, settings.SCRIPT_DIR, script_args], capture_output=True,
                                    text=True)
            if result.returncode == 0:
                script_output = json.loads(result.stdout)
                if script_output.get('code') == 200:
                    return True, script_output
                else:
                    return False, script_output.get('msg')
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        # Call script before saving to the database
        script_args = json.dumps({
            "c": "group",
            "a": "create_group",
            "data": {
                "group_name": data['name']  # assuming 'name' is the group name field
            }
        })
        success, message = self.call_script(script_args)
        if success:
            self.perform_create(serializer)
            return Response({'success': True, 'groups': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()
        new_group_name = data.get('name')

        if not new_group_name:
            return Response({'success': False, 'message': 'New group name is required'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Call script before updating the database
        script_args = json.dumps({
            "c": "group",
            "a": "update_group",
            "data": {
                "old_group": instance.name,
                "new_group": new_group_name
            }
        })
        print("script_args")
        success, message = self.call_script(script_args)
        print("success", success)
        if success:
            self.perform_update(serializer)
            return Response({'success': True, 'group': serializer.data})
        else:
            return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Call script before deleting from the database
        script_args = json.dumps({
            "c": "group",
            "a": "delete_group",
            "data": {
                "group_name": instance.name
            }
        })
        success, message = self.call_script(script_args)
        if success:
            self.perform_destroy(instance)
            return Response({'success': True})
        else:
            return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'groups': serializer.data})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'success': True, 'group': serializer.data})

    @action(detail=True, methods=['get', 'post'])
    def members(self, request, pk=None):
        if request.method == 'GET':
            # print("1111")
            members = GroupMember.objects.filter(group_id=pk)
            serializer = GroupMemberSerializer(members, many=True)
            return Response({'success': True, 'members': serializer.data})

        elif request.method == 'POST':
            data = request.data.copy()
            data['group_id'] = pk
            group = self.get_object()
            user_name = request.data.get('username')
            if not user_name:
                return Response({'success': False, 'message': 'Username is required'},
                                status=status.HTTP_400_BAD_REQUEST)
            existing_member_count = GroupMember.objects.filter(group_id=pk, username=data['username']).exists()
            if existing_member_count:
                return Response({'success': False, 'errors': 'This group already has a member.'})

            script_args = json.dumps({
                "c": "group",
                "a": "add_member",
                "data": {
                    "group_name": group.name,
                    "user_name": user_name
                }
            })
            success, message = self.call_script(script_args)
            if success:
                serializer = GroupMemberSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'success': True, 'member': serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'success': False, 'message': serializer.errors},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='members/remove/(?P<member_id>[^/.]+)')
    def remove_member(self, request, pk=None, member_id=None):
        return self._remove_member(pk, member_id)

    def _remove_member(self, group_id, member_id):
        group = self.get_object()
        try:
            member = GroupMember.objects.get(group_id=group_id, id=member_id)
            user_name = member.username  # Assuming username is stored in the username field
        except GroupMember.DoesNotExist:
            return Response({'success': False, 'message': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)

        # Call script before removing member from the database
        script_args = json.dumps({
            "c": "group",
            "a": "remove_member",
            "data": {
                "group_name": group.name,
                "user_name": user_name
            }
        })
        success, message = self.call_script(script_args)
        if success:
            member.delete()
            return Response({'success': True}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

    # @action(detail=True, methods=['delete'], url_path='members/remove/(?P<member_id>[^/.]+)')
    # def remove_member(self, request, pk=None, member_id=None):
    #     group = self.get_object()
    #     try:
    #         member = GroupMember.objects.get(group_id=pk, id=member_id)
    #         user_name = member.username  # Assuming username is stored in the username field
    #     except GroupMember.DoesNotExist:
    #         return Response({'success': False, 'message': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)
    #
    #     # Call script before removing member from the database
    #     script_args = json.dumps({
    #         "c": "group",
    #         "a": "remove_member",
    #         "data": {
    #             "group_name": group.name,
    #             "user_name": user_name
    #         }
    #     })
    #     success, message = self.call_script(script_args)
    #     if success:
    #         member.delete()
    #         return Response({'success': True}, status=status.HTTP_204_NO_CONTENT)
    #     else:
    #         return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)


class RepositoryViewSet(viewsets.ModelViewSet):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer
    parser_classes = [JSONParser]

    def call_script(self, script_args):
        try:
            result = subprocess.run([settings.EDITOR_DIR, settings.SCRIPT_DIR, script_args],
                                    capture_output=True, text=True)
            print(result)
            if result.returncode == 0:
                script_output = json.loads(result.stdout)
                if script_output.get('code') == 200:
                    return True, script_output
                else:
                    return False, script_output.get('msg')
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'repositories': serializer.data})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'success': True, 'repository': serializer.data})

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        group_id = data.get('group_id')
        existing_repo = Repository.objects.filter(group_id=group_id, name=data['name']).first()
        if existing_repo:
            return Response({'success': False, 'message': 'This repo is already of the group.'})
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        group = RepositoryGroup.objects.get(id=group_id)
        script_args = json.dumps({
            "c": "repo",
            "a": "create_repo",
            "data": {
                "group": group.name,
                "name": data['name']
            }
        })
        print(script_args)
        success, message = self.call_script(script_args)
        if success:
            self.perform_create(serializer)
            return Response({'success': True, 'repository': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()
        group = RepositoryGroup.objects.get(id=data.get('group_id'))
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)

        script_args = json.dumps({
            "c": "repo",
            "a": "edit_repo",
            "data": {
                "group": group.name,
                "old_name": instance.name,
                "new_name": data['name']
            }
        })
        success, message = self.call_script(script_args)
        print(script_args)
        if success:
            self.perform_update(serializer)
            return Response({'success': True, 'repository': serializer.data})
        else:
            return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()  # 获取仓库实例
        group = RepositoryGroup.objects.get(id=instance.group_id)
        script_args = json.dumps({
            "c": "repo",
            "a": "delete_repo",
            "data": {
                "group": group.name,
                "name": instance.name
            }
        })
        success, message = self.call_script(script_args)
        print(script_args)
        if success:
            self.perform_destroy(instance)
            return Response({'success': True})
        else:
            return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def members(self, request, pk=None):
        if request.method == 'GET':
            members = RepositoryMember.objects.filter(repository_id=pk)
            serializer = RepositoryMemberSerializer(members, many=True)
            return Response({'success': True, 'members': serializer.data})

        elif request.method == 'POST':
            data = request.data.copy()
            data['repository_id'] = pk
            instance = self.get_object()
            group = RepositoryGroup.objects.get(id=instance.group_id)
            existing_member = RepositoryMember.objects.filter(repository_id=pk, username=data['username']).first()
            members = RepositoryMember.objects.filter(repository_id=pk).all()
            if existing_member:
                return Response({'success': False, 'errors': 'This user is already a member of the repository.'})
            user_list = []
            for member in members:
                user_list.append(member.username)
            user_list.append(data["username"])
            script_args = json.dumps({
                "c": "apache",
                "a": "add_user",
                "data": {
                    "group": group.name,
                    "name": instance.name,
                    "users": user_list
                }
            })
            success, message = self.call_script(script_args)
            print(script_args)
            if success:
                serializer = RepositoryMemberSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'success': True, 'member': serializer.data}, status=status.HTTP_201_CREATED)
                else:

                    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='members/remove/(?P<member_id>[^/.]+)')
    def remove_member(self, request, pk=None, member_id=None):
        try:
            instance = self.get_object()
            group = RepositoryGroup.objects.get(id=instance.group_id)
            member = RepositoryMember.objects.get(id=member_id, repository_id=pk)
            user_list = []
            members = RepositoryMember.objects.filter(repository_id=pk).all()
            for member in members:
                user_list.append(member.username)
            user_list.remove(member.username)
            print(user_list)
            script_args = json.dumps({
                "c": "apache",
                "a": "add_user",
                "data": {
                    "group": group.name,
                    "name": instance.name,
                    "users": user_list
                }
            })
            success, message = self.call_script(script_args)
            print(script_args)
            if success:
                member.delete()
                return Response({'success': True}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)
        except RepositoryMember.DoesNotExist:
            return Response({'success': False, 'message': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)


class ServerIpViewSet(viewsets.ViewSet):
    def list(self, request):
        import socket
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return Response({'success': True, 'ip': ip_address})


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    def list(self, request):
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response({'success': True, 'roles': serializer.data})


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'])
    def list_usernames(self, request):
        users = CustomUser.objects.all().values_list('username', flat=True)
        return Response({'success': True, 'users': list(users)})


class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    parser_classes = [JSONParser]

    def call_script(self, script_args):
        try:
            result = subprocess.run([settings.EDITOR_DIR, settings.SCRIPT_DIR, script_args], capture_output=True,
                                    text=True)
            if result.returncode == 0:
                script_output = json.loads(result.stdout)
                if script_output.get('code') == 200:
                    return True, script_output
                else:
                    return False, script_output.get('msg')
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)

    def list(self, request, *args, **kwargs):
        repository_id = request.query_params.get('repository_id', None)
        if repository_id is not None:
            queryset = self.get_queryset().filter(repository_id=repository_id)
        else:
            queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'branches': serializer.data})

    #  GET /api/branches/1/ 会调用 retrieve 方法来获取 id 为 1 的分支的信息
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'success': True, 'branch': serializer.data})

    def create(self, request, *args, **kwargs):
        repository_name = request.data.get('repository_name')
        repository_group_name = request.data.get('repository_group_name')  # 获取仓库组名

        try:
            # 根据仓库组名获取仓库组
            repository_group = RepositoryGroup.objects.get(name=repository_group_name)

            # 根据仓库组ID和仓库名查找仓库
            repository = Repository.objects.get(name=repository_name, group_id=repository_group.id)

            request.data['repository_id'] = repository.id
            request.data['repository_group_id'] = repository_group.id  # 设置仓库组ID
        except RepositoryGroup.DoesNotExist:
            return Response({'success': False, 'message': 'Repository group not found.'})
        except Repository.DoesNotExist:
            return Response({'success': False, 'message': 'Repository not found or not unique.'})
        except Exception as e:
            return Response({'success': False, 'message': str(e)})

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(repository_group.name, repository.name, request.data['name'])
        # Check for uniqueness of branch name within the repository
        branch_name = request.data.get('name')
        if Branch.objects.filter(name=branch_name, repository_id=repository.id).exists():
            return Response({'success': False, 'message': 'Branch with this name already exists in the repository.'})

        script_args = json.dumps({
            "c": "repo",
            "a": "create_branch",
            "data": {
                "group": repository_group.name,
                "repo_name": repository.name,
                "branch_name": request.data['name']
            }
        })
        success, message = self.call_script(script_args)
        print(script_args)
        if success:
            self.perform_create(serializer)
            return Response({'success': True, 'branch': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            # 获取仓库和仓库组信息
            repository = Repository.objects.get(id=instance.repository_id)
            repository_group = RepositoryGroup.objects.get(id=repository.group_id)
        except Repository.DoesNotExist:
            return Response({'success': False, 'message': 'Repository not found.'})
        except RepositoryGroup.DoesNotExist:
            return Response({'success': False, 'message': 'Repository group not found.'})
        except Exception as e:
            return Response({'success': False, 'message': str(e)})

        # 准备删除分支的脚本参数
        script_args = json.dumps({
            "c": "repo",
            "a": "delete_branch",
            "data": {
                "group": repository_group.name,
                "repo_name": repository.name,
                "branch_name": instance.name
            }
        })

        # 调用删除分支的脚本
        success, message = self.call_script(script_args)
        if success:
            # 脚本成功执行后，删除数据库中的分支记录
            self.perform_destroy(instance)
            return Response({'success': True})
        else:
            return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        repository_name = request.data.get('repository_name')
        repository_group_name = request.data.get('repository_group_name')
        new_branch_name = request.data.get('name')

        try:
            repository_group = RepositoryGroup.objects.get(name=repository_group_name)
            repository = Repository.objects.get(name=repository_name, group_id=repository_group.id)
            request.data['repository_id'] = repository.id
            request.data['repository_group_id'] = repository_group.id
        except Repository.DoesNotExist:
            return Response({'success': False, 'message': f'Repository "{repository_name}" not found'})

        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        old_branch_name = instance.name  # 获取旧的分支名称
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        script_args = json.dumps({
            "c": "repo",
            "a": "rename_branch",
            "data": {
                "group": repository_group.name,
                "repo_name": repository.name,
                "old_name": old_branch_name,
                "new_name": new_branch_name
            }
        })

        success, message = self.call_script(script_args)
        print(script_args)
        if success:
            self.perform_update(serializer)
            return Response({'success': True, 'branch': serializer.data})
        else:
            return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def members(self, request, pk=None):
        if request.method == 'GET':
            members = BranchMember.objects.filter(branch_id=pk)
            serializer = BranchMemberSerializer(members, many=True)
            return Response({'success': True, 'members': serializer.data})

        elif request.method == 'POST':
            return self._handle_member_update(request, pk, add=True)

    @action(detail=True, methods=['delete'], url_path='members/remove/(?P<member_id>[^/.]+)')
    def remove_member(self, request, pk=None, member_id=None):
        return self._handle_member_update(request, pk, member_id, add=False)

    def update_all_branches(self):
        branches = Branch.objects.all()
        branch_groups = {}

        # 分组分支
        for branch in branches:
            key = (branch.repository_group_id, branch.repository_id)
            if key not in branch_groups:
                branch_groups[key] = []
            branch_groups[key].append(branch)

        for key, branches in branch_groups.items():
            repository_group_id, repository_id = key

            try:
                repository_group = RepositoryGroup.objects.get(id=repository_group_id)
                repository = Repository.objects.get(id=repository_id)
            except RepositoryGroup.DoesNotExist:
                print(f'Repository group with ID {repository_group_id} not found.')
                continue
            except Repository.DoesNotExist:
                print(f'Repository with ID {repository_id} not found.')
                continue

            branches_configs = []
            for branch in branches:
                users = list(
                    BranchMember.objects.filter(branch_id=branch.id, role_id=1).values_list('username', flat=True))
                # if not users:
                #     continue
                push_urls = list(Hook.objects.filter(
                    repository_group_id=repository_group_id,
                    repository_id=repository_id,
                    branch_name=branch.name,
                    trigger_event='push'
                ).values_list('hook_url', flat=True))

                branches_configs.append({
                    "branch": branch.name,
                    "urls": push_urls,
                    "users": users
                })

            script_args = json.dumps({
                "c": "add_hook",
                "a": "add_hook",
                "data": {
                    "group": repository_group.name,
                    "repo": repository.name,
                    "branches_configs": branches_configs,
                    "hook_type": "pre-receive"
                }
            })

            success, script_message = self.call_script(script_args)
            if success:
                print(f'Successfully updated hooks for repository {repository.name} in group {repository_group.name}')
            else:
                print(
                    f'Failed to update hooks for repository {repository.name} in group {repository_group.name}: {script_message}')

    def _handle_member_update(self, request, pk, member_id=None, add=True):
        data = request.data.copy()
        data['branch_id'] = pk

        if add:
            existing_member = BranchMember.objects.filter(branch_id=pk, username=data['username']).first()
            if existing_member:
                return Response({'success': False, 'errors': 'This user is already a member of the branch.'})
            serializer = BranchMemberSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                message = 'member added successfully'
            else:
                return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                member = BranchMember.objects.get(id=member_id, branch_id=pk)
                member.delete()
                message = 'member removed successfully'
            except BranchMember.DoesNotExist:
                return Response({'success': False, 'message': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)

        self.update_all_branches()
        return Response({'success': True, 'message': message})


class HookViewSet(viewsets.ModelViewSet):
    queryset = Hook.objects.all()
    serializer_class = HookSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'hooks': serializer.data})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'success': True, 'hook': serializer.data})

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        try:
            repository_group = RepositoryGroup.objects.get(name=data.get('repository_group_name'))
            repository = Repository.objects.get(name=data.get('repository_name'), group_id=repository_group.id)
            data['repository_group_id'] = repository_group.id
            data['repository_id'] = repository.id
        except RepositoryGroup.DoesNotExist:
            return Response({'success': False, 'message': 'Repository group not found.'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Repository.DoesNotExist:
            return Response({'success': False, 'message': 'Repository not found.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        self.update_all_branches()
        return Response({'success': True, 'hook': serializer.data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()
        try:
            repository_group = RepositoryGroup.objects.get(name=data.get('repository_group_name'))
            repository = Repository.objects.get(name=data.get('repository_name'), group_id=repository_group.id)
            data['repository_group_id'] = repository_group.id
            data['repository_id'] = repository.id
        except RepositoryGroup.DoesNotExist:
            return Response({'success': False, 'message': 'Repository group not found.'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Repository.DoesNotExist:
            return Response({'success': False, 'message': 'Repository not found.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        self.update_all_branches()
        return Response({'success': True, 'hook': serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        self.update_all_branches()
        return Response({'success': True})

    @action(detail=True, methods=['post'])
    def test_hook(self, request, pk=None):

        hook = self.get_object()
        try:
            response = requests.post(
                hook.hook_url,
                json={"event": hook.trigger_event, "branch_name": hook.branch_name}
            )
            if response.status_code == 200:
                return Response({'success': True, 'message': 'Hook tested successfully'})
            else:
                return Response(
                    {'success': False, 'message': f'Hook test failed with status code {response.status_code}'},
                    status=status.HTTP_400_BAD_REQUEST)
        except requests.exceptions.RequestException as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # http://localhost:8000/api/webhook-trigger-records/
    def update_all_branches(self):
        branches = Branch.objects.all()
        branch_groups = {}

        # 分组分支
        for branch in branches:
            key = (branch.repository_group_id, branch.repository_id)
            if key not in branch_groups:
                branch_groups[key] = []
            branch_groups[key].append(branch)

        for key, branches in branch_groups.items():
            repository_group_id, repository_id = key

            try:
                repository_group = RepositoryGroup.objects.get(id=repository_group_id)
                repository = Repository.objects.get(id=repository_id)
            except RepositoryGroup.DoesNotExist:
                print(f'Repository group with ID {repository_group_id} not found.')
                continue
            except Repository.DoesNotExist:
                print(f'Repository with ID {repository_id} not found.')
                continue

            branches_configs = []
            hook_type = "pre-receive"
            for branch in branches:
                users = list(
                    BranchMember.objects.filter(branch_id=branch.id, role_id=1).values_list('username', flat=True))
                hooks = Hook.objects.filter(repository_group_id=repository_group_id, repository_id=repository_id,
                                            branch_name=branch.name)
                # urls = [hook.hook_url for hook in hooks if hook.trigger_event == 'push']
                urls = list(Hook.objects.filter(
                    repository_group_id=repository_group_id,
                    repository_id=repository_id,
                    branch_name=branch.name,
                ).values_list('hook_url', flat=True))
                # if hook.trigger_event == 'pull':
                urls.append(settings.HOOK_URL)
                branches_configs.append({
                    "branch": branch.name,
                    "urls": urls,
                    "users": users
                })

            script_args = json.dumps({
                "c": "add_hook",
                "a": "add_hook",
                "data": {
                    "group": repository_group.name,
                    "repo": repository.name,
                    "branches_configs": branches_configs,
                    "hook_type": "pre-receive"
                }
            })

            success, script_message = self.call_script(script_args)
            if success:
                print(f'Successfully updated hooks for repository {repository.name} in group {repository_group.name}')
            else:
                print(
                    f'Failed to update hooks for repository {repository.name} in group {repository_group.name}: {script_message}')

    def call_script(self, script_args):
        try:
            result = subprocess.run([settings.EDITOR_DIR, settings.SCRIPT_DIR, script_args], capture_output=True,
                                    text=True)
            if result.returncode == 0:
                script_output = json.loads(result.stdout)
                if script_output.get('code') == 200:
                    return True, script_output
                else:
                    return False, script_output.get('msg')
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)


from concurrent.futures import ThreadPoolExecutor


class ImportRepositoryViewSet(viewsets.ModelViewSet):
    executor = ThreadPoolExecutor(max_workers=5)
    queryset = ImportedRepository.objects.all()
    serializer_class = ImportRepositorySerializer

    def clone_repository(self, url, username, password):
        try:
            repo_name = url.split('/')[-1].replace('.git', '')
            clone_path = f'/var/www/html/git/{repo_name}.git'
            command = ['git', 'clone', '--bare', url, clone_path]
            if username and password:
                url_with_auth = url.replace('https://', f'https://{username}:{password}@')
                command = ['git', 'clone', '--bare', url_with_auth, clone_path]

            subprocess.run(command, check=True)
            return {'success': True}
        except subprocess.CalledProcessError as e:
            return {'success': False, 'message': str(e)}

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        url = data.get("url")
        username = data.get("username")
        password = data.get("password")
        self.executor.submit(self.clone_repository, url, username, password)
        # self.clone_repository(url, username, password)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # Handle the repository import logic here, e.g., cloning the repo
        # import_repository(serializer.data)
        return Response({'success': True, 'repository': serializer.data}, status=status.HTTP_201_CREATED)


class WebhookTriggerRecordViewSet(viewsets.ModelViewSet):
    queryset = WebhookTriggerRecord.objects.all()
    serializer_class = WebhookTriggerRecordSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'hooks': serializer.data})

    def create(self, request, *args, **kwargs):
        print("request.data==", request.data)
        data = request.data.copy()

        # 获取数据并设置默认值
        hook_url = data.get('hook_url', '')
        event = data.get('event', '')
        branch = data.get('branch', '')
        status = data.get('status', '')
        response_content = data.get('response_content', '')

        # 创建新的 WebhookTriggerRecord 实例
        record = WebhookTriggerRecord.objects.create(
            hook_url=hook_url,
            event=event,
            branch=branch,
            status=status,
            response_content=response_content
        )

        return Response({'success': True, 'record': {
            "id": record.id,
            "hook_url": record.hook_url,
            "event": record.event,
            "branch": record.branch,
            "status": record.status,
            "trigger_time": record.trigger_time,
            "response_content": record.response_content
        }})


class TestHookViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'])
    def test(self, request):
        # 你可以在这里添加任何测试逻辑
        return Response({'success': True, 'message': 'Test hook executed successfully'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def test(self, request):
        print("TestHookViewSet")
        # 你可以在这里添加任何测试逻辑
        return Response({'success': True, 'message': 'Test hook executed successfully'}, status=status.HTTP_200_OK)
