from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from django.conf import settings
import json
import subprocess
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
        group = self.get_object()
        try:
            member = GroupMember.objects.get(group_id=pk, id=member_id)
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
        try:
            repository = Repository.objects.get(name=repository_name)
            repository_group = RepositoryGroup.objects.get(id=repository.group_id)
            request.data['repository_id'] = repository.id
        except Exception as e:
            return Response({'success': False, 'message': str(e)})

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
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
            repository = Repository.objects.get(id=instance.repository_id)
            repository_group = RepositoryGroup.objects.get(id=repository.group_id)
        except Exception as e:
            return Response({'success': False, 'message': str(e)})

        script_args = json.dumps({
            "c": "repo",
            "a": "delete_branch",
            "data": {
                "group": repository_group.name,
                "repo_name": repository.name,
                "branch_name": instance.name
            }
        })
        success, message = self.call_script(script_args)
        if success:
            self.perform_destroy(instance)
            return Response({'success': True})
        else:
            return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        repository_name = request.data.get('repository_name')
        try:
            repository = Repository.objects.get(name=repository_name)
            request.data['repository_id'] = repository.id
        except Repository.DoesNotExist:
            return Response({'success': False, 'errors': f'Repository "{repository_name}" not found'})

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'success': True, 'branch': serializer.data})

    @action(detail=True, methods=['get', 'post'])
    def members(self, request, pk=None):
        if request.method == 'GET':
            members = BranchMember.objects.filter(branch_id=pk)
            serializer = BranchMemberSerializer(members, many=True)
            return Response({'success': True, 'members': serializer.data})

        elif request.method == 'POST':
            data = request.data.copy()
            data['branch_id'] = pk
            existing_member = BranchMember.objects.filter(branch_id=pk, username=data['username']).first()
            if existing_member:
                return Response({'success': False, 'errors': 'This user is already a member of the branch.'})

            serializer = BranchMemberSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({'success': True, 'member': serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='members/remove/(?P<member_id>[^/.]+)')
    def remove_member(self, request, pk=None, member_id=None):
        try:
            member = BranchMember.objects.get(id=member_id, branch_id=pk)
            member.delete()
            return Response({'success': True}, status=status.HTTP_204_NO_CONTENT)
        except BranchMember.DoesNotExist:
            return Response({'success': False, 'message': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)


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
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'success': True, 'hook': serializer.data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'success': True, 'hook': serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'success': True})

    @action(detail=True, methods=['post'])
    def test_hook(self, request, pk=None):
        hook = self.get_object()
        # 在这里实现 Hook 测试逻辑，例如发送请求到 hook_url
        return Response({'success': True, 'message': 'Hook tested successfully'})


class ImportRepositoryViewSet(viewsets.ModelViewSet):
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
        self.clone_repository(url, username, password)
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
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'record': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
