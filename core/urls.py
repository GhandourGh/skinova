from django.urls import path
from . import views

urlpatterns = [
    path('<int:client_id>/profile/', views.client_profile, name='client_profile'),
    path('package/<int:client_package_id>/add-session/', views.add_package_session, name='add_package_session'),
    path('service/<int:service_session_id>/add-session/', views.add_service_session, name='add_service_session'),
    path('<int:client_id>/assign-package/', views.assign_package_to_client, name='assign_package_to_client'),
    path('<int:client_id>/start-service/', views.start_service_session, name='start_service_session'),
    path('service-session/<int:service_session_id>/delete/', views.delete_service_session, name='delete_service_session'),
    path('client-package/<int:client_package_id>/delete/', views.delete_client_package, name='delete_client_package'),
    # Backup management
    path('backup/', views.backup_management, name='backup_management'),
    path('backup/create/', views.create_backup, name='create_backup'),
    path('backup/download/<str:backup_name>/', views.download_backup, name='download_backup'),
    path('backup/delete/<str:backup_name>/', views.delete_backup, name='delete_backup'),
]

