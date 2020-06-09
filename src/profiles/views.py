from django.http import *
from .models import UserProfile
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from profiles.forms import RegistrationForm, LoginForm, ProjectForm, TicketForm
from django.contrib.auth.forms import AuthenticationForm
from profiles.models import UserProfile, Project, Ticket

# Create your views here.

def login_page(request):
    context = {}
    user = request.user

    # user is already logged in, redirect back to dashboard
    if user.is_authenticated:
        return redirect("dashboard")

    # user is trying to log in
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)

            if user:
                login(request, user)
                return redirect("dashboard")

    else:
        form = LoginForm()

    context['login_form'] = form
    return render(request, 'login.html', context)


@login_required
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


@login_required
def dashboard(request):
    context = {}
    return render(request, 'dashboard.html', context)


@login_required
def tickets(request):
    context = {}
    user_projects = Project.objects.filter(users__id=request.user.id)
    user_tickets = Ticket.objects.filter(project_id__in=user_projects)
    context['user_tickets'] = user_tickets
    return render(request, 'tickets.html', context)


@login_required
def projects(request):
    context = {}
    user_projects = Project.objects.filter(users__id=request.user.id)
    context['user_projects'] = user_projects
    return render(request, 'projects.html', context)


@login_required
def new_ticket(request):
    form = TicketForm(request.POST, user_id=request.user.id)
    if form.is_valid():
        form.save()
        return redirect("tickets")

    context = {
        'new_ticket_form': form
    }

    return render(request, "new_ticket.html", context)


@login_required
def new_project(request):
    form = ProjectForm(request.POST)
    if form.is_valid():
        project = form.save()
        project.users.add(request.user)
        return redirect("projects")

    context = {
        'new_project_form': form
    }

    return render(request, "new_project.html", context)
    