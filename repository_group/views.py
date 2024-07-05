from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import RepositoryGroup, GroupMember, Repository
from .serializers import RepositoryGroupSerializer, GroupMemberSerializer, RepositorySerializer

from rest_framework.parsers import JSONParser


class RepositoryGroupViewSet(viewsets.ModelViewSet):
    queryset = RepositoryGroup.objects.all()
    serializer_class = RepositoryGroupSerializer
    parser_classes = [JSONParser]

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
            print("1111")
            members = GroupMember.objects.filter(group_id=pk)
            serializer = GroupMemberSerializer(members, many=True)
            return Response({'success': True, 'members': serializer.data})

        elif request.method == 'POST':
            data = request.data.copy()
            data['group_id'] = pk
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


from rest_framework.decorators import api_view


@api_view(['GET'])
def get_server_ip(request):
    import socket
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return Response({'success': True, 'ip': ip_address})
