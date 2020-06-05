from django.http import *
from .models import UserProfile
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from profiles.forms import RegistrationForm

# Create your views here.

def login_page(request):
    return render(request, 'login.html')


def logout_user(request):
    print(1)


def register_page(request):
    context = {}
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user_profile = authenticate(email=email, password=raw_password)
            login(request, user_profile)
            return redirect('dashboard')
        else:
            context['registration_form'] = form
    
    else: # GET REQUEST
        form = RegistrationForm()
        context['registration_form'] = form

    return render(request, 'register.html', context)


def dashboard(request):
    return render(request, 'dashboard.html')


def tickets(request):
    return render(request, 'tickets.html')


def projects(request):
    return render(request, 'projects.html')


def new_ticket(request):
    return render(request, 'new_ticket.html')
    