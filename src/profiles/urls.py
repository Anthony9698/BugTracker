from django.urls import path
from django.contrib import admin
from profiles import views

urlpatterns = [
    path('', views.login_page, name='login'),
    path('admin/', admin.site.urls),
    path('admin-user-view/', views.admin_user_view, name="admin_user_view"),
    path('admin-user-view/edit/<str:pk>/', views.edit_roles, name="edit_role"),
    path('demo/', views.demo, name='demo'),
    path('register/', views.register_page, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tickets/', views.tickets, name='tickets'),
    path('tickets/create', views.new_ticket, name='new_ticket'),
    path('tickets/detail/<str:pk>/', views.ticket_detail, name='ticket_detail'),
    path('tickets/edit/<str:pk>/', views.edit_ticket, name='edit_ticket'),
    path('tickets/assign-user/<str:pk>/', views.assign_ticket, name="assign_ticket"),
    path('ticket-comments/ticket-id/<str:pk>/', views.new_comment, name="new_comment"),
    path('ticket-comments/delete/<str:pk>/', views.delete_comment, name="delete_comment"),
    path('ticket-comments/edit/<str:pk>/', views.edit_comment, name="edit_comment"),
    path('tickets/history/<str:pk>/', views.ticket_history, name="ticket_history"),
    path('projects/', views.projects, name='projects'),
    path('projects/create', views.new_project, name="new_project"),
    path('projects/detail/<str:pk>/', views.project_detail, name='project_detail'),
    path('projects/edit/<str:pk>/', views.edit_project, name="edit_project"),
    path('projects/archived-projects', views.archived_projects, name="archived_projects"),
    path('projects/archive/<str:pk>/', views.archive_project, name="archive_project"),
    path('project-user-view/edit/<str:pk>/', views.assign_users, name="assign_users"),
    path('manage', views.manage_profile, name="manage_profile"),
    path('manage/edit-settings/', views.edit_profile, name="edit_profile"),
    path('manage/change-password/', views.change_password, name="change_password"),
]