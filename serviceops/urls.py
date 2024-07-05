from django.urls import path
from . import views

urlpatterns = [
    path('', views.service_operations, name='service_operations'),
    path('start/', views.start_service, name='start_service'),
    path('stop/', views.stop_service, name='stop_service'),
    path('refresh/', views.refresh_service_status, name='refresh_service_status'),
]
