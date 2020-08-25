"""bugtracker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from profiles import views as profile_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', profile_views.register_page, name='register'),
    path('demo/', profile_views.demo, name='demo'),
    path('logout/', profile_views.logout_request, name='logout'),
    path('', profile_views.login_page, name='login'),
    path('tickets/', profile_views.tickets, name='tickets'),
    path('projects/', profile_views.projects, name='projects'),
    path('dashboard/', profile_views.dashboard, name='dashboard'),
    path('tickets/create', profile_views.new_ticket, name='new_ticket'),
    path('tickets/detail/<str:pk>/', profile_views.ticket_detail, name='ticket_detail'),
    path('tickets/edit/<str:pk>/', profile_views.edit_ticket, name='edit_ticket'),
    path('projects/create', profile_views.new_project, name="new_project"),
    path('projects/detail/<str:pk>/', profile_views.project_detail, name='project_detail'),
    path('projects/edit/<str:pk>/', profile_views.edit_project, name="edit_project"),
    path('projects/archived-projects', profile_views.archived_projects, name="archived_projects"),
    path('projects/archive/<str:pk>/', profile_views.archive_project, name="archive_project"),
    path('admin-user-view/', profile_views.admin_user_view, name="admin_user_view"),
    path('admin-user-view/edit/<str:pk>/', profile_views.edit_roles, name="edit_role"),
    path('project-user-view/edit/<str:pk>/', profile_views.assign_users, name="assign_users"),
    path('tickets/assign-user/<str:pk>/', profile_views.assign_ticket, name="assign_ticket"),
    path('ticket-comments/ticket-id/<str:pk>/', profile_views.new_comment, name="new_comment"),
    path('ticket-comments/delete/<str:pk>/', profile_views.delete_comment, name="delete_comment"),
    path('ticket-comments/edit/<str:pk>/', profile_views.edit_comment, name="edit_comment"),
    path('tickets/history/<str:pk>/', profile_views.ticket_history, name="ticket_history"),
    path('manage', profile_views.manage_profile, name="manage_profile"),
    path('manage/edit-settings/', profile_views.edit_profile, name="edit_profile"),
    path('manage/change-password/', profile_views.change_password, name="change_password"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)