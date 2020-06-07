from django.http import *
from .models import UserProfile
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from profiles.forms import RegistrationForm, LoginForm
from django.contrib.auth.forms import AuthenticationForm

# Create your views here.

def login_page(request):
    context = {}
    user = request.user

    # # user is already logged in, redirect back to dashboard
    # if user.is_authenticated:
    #     return redirect("dashboard")

    # user is trying to log in
    if request.POST:
        if request.POST.get("login"):
            form = LoginForm(request.POST)
            if form.is_valid():
                email = request.POST['email']
                password = request.POST['password']
                user = authenticate(email=email, password=password)

                if user:
                    login(request, user)
                    return redirect("dashboard")
        elif request.POST.get("forgot_ep"):
            return redirect("login")
        
        elif request.POST.get("sign_up"):
            print(2)
            return redirect("register")

    else:
        form = LoginForm()

    context['login_form'] = form
    return render(request, 'login.html', context)


def logout_request(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("login")


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
    