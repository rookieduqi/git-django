from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser

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

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'success': True, 'groups': serializer.data}, status=status.HTTP_201_CREATED)

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
            existing_member_count = GroupMember.objects.filter(group_id=pk, username=data['username']).exists()
            if existing_member_count:
                return Response({'success': False, 'errors': 'This group already has a member.'})
            serializer = GroupMemberSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({'success': True, 'member': serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='members/remove/(?P<member_id>[^/.]+)')
    def remove_member(self, request, pk=None, member_id=None):
        try:
            member = GroupMember.objects.get(id=member_id, group_id=pk)
            member.delete()
            return Response({'success': True}, status=status.HTTP_204_NO_CONTENT)
        except GroupMember.DoesNotExist:
            return Response({'success': False, 'message': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'success': True, 'group': serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'success': True})


class RepositoryViewSet(viewsets.ModelViewSet):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer
    parser_classes = [JSONParser]

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
        # data['url'] = f"http://repository/{data['name']}"
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'success': True, 'repository': serializer.data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'success': True, 'repository': serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'success': True})

    @action(detail=True, methods=['get', 'post'])
    def members(self, request, pk=None):
        if request.method == 'GET':
            members = RepositoryMember.objects.filter(repository_id=pk)
            serializer = RepositoryMemberSerializer(members, many=True)
            return Response({'success': True, 'members': serializer.data})

        elif request.method == 'POST':
            data = request.data.copy()
            data['repository_id'] = pk
            existing_member = RepositoryMember.objects.filter(repository_id=pk, username=data['username']).first()
            if existing_member:
                return Response({'success': False, 'errors': 'This user is already a member of the repository.'})

            serializer = RepositoryMemberSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({'success': True, 'member': serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='members/remove/(?P<member_id>[^/.]+)')
    def remove_member(self, request, pk=None, member_id=None):
        try:
            member = RepositoryMember.objects.get(id=member_id, repository_id=pk)
            member.delete()
            return Response({'success': True}, status=status.HTTP_204_NO_CONTENT)
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


from user.models import CustomUser


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

    def list(self, request, *args, **kwargs):
        repository_id = request.query_params.get('repository_id', None)
        if repository_id is not None:
            queryset = self.get_queryset().filter(repository_id=repository_id)
        else:
            queryset = self.get_queryset()
        # queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'branches': serializer.data})

    #  GET /api/branches/1/ 会调用 retrieve 方法来获取 id 为 1 的分支的信息
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'success': True, 'branch': serializer.data})

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        repository_id = data.get('repository_id')
        branch_name = data.get('name')
        if Branch.objects.filter(repository_id=repository_id, name=branch_name).exists():
            return Response({'success': False, 'errors': 'This branch name already exists in the repository.'})
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'success': True, 'branch': serializer.data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'success': True, 'branch': serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'success': True})

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

    def create(self, request, *args, **kwargs):
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
