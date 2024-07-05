# myapp/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RepositoryGroupViewSet, RepositoryViewSet
from .views import get_server_ip

router = DefaultRouter()
router.register(r'repository_groups', RepositoryGroupViewSet, basename='repositorygroup')
router.register(r'repositories', RepositoryViewSet, basename='repository')

urlpatterns = [
    path('', include(router.urls)),
    path('get_server_ip/', get_server_ip, name='get_server_ip'),
]
