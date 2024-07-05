from django.urls import path
from . import views

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from .views import UserViewSet, RoleViewSet, RepositoryMemberViewSet

# router = DefaultRouter()
# router.register(r'users', UserViewSet, basename='user')
# router.register(r'roles', RoleViewSet, basename='role')
# router.register(r'repository_members', RepositoryMemberViewSet, basename='repository_member')

urlpatterns = [
    path('', views.login),
    path('login/', views.login, name='login'),
    path('home/', views.home, name='home'),
    # path('user_management/', views.UserManagementView.as_view(), name='user_management'),

    path('list/', views.user_list, name='user_list'),
    path('add/', views.add_user, name='add_user'),
    path('edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('reset_password/<int:user_id>/', views.reset_password, name='reset_password'),
    path('delete/<int:user_id>/', views.delete_user, name='delete_user'),

    # path('api/', include(router.urls)),
]
