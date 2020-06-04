from django.http import *
from .models import UserProfile
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.

def login_page(request):
    return render(request, 'login.html')


def logout_user(request):
    print(1)


def register_page(request):
    return render(request, 'register.html')


def dashboard(request):
    return render(request, 'dashboard.html')


def tickets(request):
    return render(request, 'tickets.html')


def projects(request):
    return render(request, 'projects.html')


def new_ticket(request):
    return render(request, 'new_ticket.html')
    