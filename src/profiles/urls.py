from django.urls import path
from profiles import views

urlpatterns = [
    path('', views.login_page, name='login'),
    path('logout/', views.logout_request, name='logout'),
    path('register/', views.register_page, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tickets/', views.tickets, name='tickets'),
    path('tickets/create', views.new_ticket, name='new_ticket'),
    path('projects/', views.projects, name='projects'),
    path('projects/create', views.new_project, name="new_project"),
]