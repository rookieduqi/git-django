# myapp/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RepositoryGroupViewSet, RepositoryViewSet
from .views import ServerIpViewSet

router = DefaultRouter()
router.register(r'repository_groups', RepositoryGroupViewSet, basename='repositorygroup')
router.register(r'repositories', RepositoryViewSet, basename='repository')
router.register(r'get_server_ip', ServerIpViewSet, basename='get_server_ip')

urlpatterns = [
    path('', include(router.urls)),
]
