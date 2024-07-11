# myapp/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RepositoryGroupViewSet, RepositoryViewSet, RoleViewSet, UserViewSet, BranchViewSet, HookViewSet, \
    ImportRepositoryViewSet, WebhookTriggerRecordViewSet, TestHookViewSet
from .views import ServerIpViewSet

router = DefaultRouter()
router.register(r'repository_groups', RepositoryGroupViewSet, basename='repositorygroup')
router.register(r'repositories', RepositoryViewSet, basename='repository')
router.register(r'get_server_ip', ServerIpViewSet, basename='get_server_ip')

router.register(r'users', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')

router.register(r'branches', BranchViewSet, basename='branch')

router.register(r'hooks', HookViewSet, basename='hook')
router.register(r'test-hooks', TestHookViewSet, basename='test-hooks')

router.register(r'import-repository', ImportRepositoryViewSet, basename='importrepository')

router.register(r'webhook-trigger-records', WebhookTriggerRecordViewSet, basename='webhooktriggerrecord')

urlpatterns = [
    path('', include(router.urls)),
]
