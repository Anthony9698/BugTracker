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
    path('adminuserview', profile_views.admin_user_view, name="admin_user_view")
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)