from django.urls import path
from api import views

urlpatterns = [
    path('overview/', views.api_overview, name="api_overview"),
]