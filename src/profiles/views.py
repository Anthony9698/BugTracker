from django.http import *
from .models import UserProfile
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from profiles.forms import RegistrationForm, LoginForm, ProjectForm, TicketForm,\
    UserRolesForm, AddProjectUsersForm, RemoveProjectUsersForm, AssignTicketUserForm,\
    CommentForm
from django.contrib.auth.forms import AuthenticationForm
from profiles.models import UserProfile, Project, Ticket, Comment, TicketAuditTrail
from django.http import HttpResponseNotFound
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
    return render(request, 'user/login.html', context)


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

    return render(request, 'user/register.html', context)


@login_required
def dashboard(request):
    user_projects = Project.objects.filter(users__id=request.user.id)
    user_tickets = Ticket.objects.filter(project__in=user_projects).order_by('-last_modified_date')
    project_paginator = Paginator(user_projects, 5)
    page = request.GET.get('page')

    try:
        projects = project_paginator.page(page)

    except PageNotAnInteger:
        projects = project_paginator.page(1)

    except EmptyPage:
        projects = project_paginator.page(project_paginator.num_pages)

    project_tickets_dict = {}
    critical_tickets_dict = {}
    resolved_tickets_dict = {}
    for proj in projects:
        project_tickets = Ticket.objects.filter(project=proj.id).count()
        critical_tickets = Ticket.objects.filter(Q(project=proj.id) & Q(priority__exact='Critical')).count()
        resolved_tickets = Ticket.objects.filter(Q(project=proj.id) & Q(status__exact='Resolved')).count()
        project_tickets_dict[proj.id] = project_tickets
        critical_tickets_dict[proj.id] = critical_tickets
        resolved_tickets_dict[proj.id] = resolved_tickets

    context = {
        'user_tickets': user_tickets,
        'user_projects': user_projects,
        'projects': projects,
        'project_tickets_dict': project_tickets_dict,
        'critical_tickets_dict': critical_tickets_dict,
        'resolved_tickets_dict': resolved_tickets_dict
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def tickets(request):
    context = {}
    user_projects = Project.objects.filter(users__id=request.user.id)
    user_tickets = Ticket.objects.filter(project__in=user_projects)
    context['user_tickets'] = user_tickets
    return render(request, 'ticket/tickets.html', context)


@login_required
def projects(request):
    context = {}
    
    # display all unarchived projects here if you are admin
    if request.user.is_admin:
        user_projects = Project.objects.filter(archived=False)
    
    else:
        user_projects = Project.objects.filter(Q(users__id=request.user.id) & Q(archived=False))

    context['user_projects'] = user_projects
    return render(request, 'project/projects.html', context)


@login_required
def new_ticket(request):
    form = TicketForm(request.user, request.POST, instance=None)
    if form.is_valid():
        ticket = form.save(commit=False)
        ticket.owner = request.user
        ticket.save()
        return redirect("tickets")

    context = {
        'new_ticket_form': form
    }

    return render(request, "ticket/new_ticket.html", context)


@login_required
def ticket_detail(request, pk):
    _ticket = Ticket.objects.get(pk=pk)
    ticket_comments = Comment.objects.filter(ticket=_ticket.id)
    paginator = Paginator(ticket_comments, 2)
    page = request.GET.get('page')

    try:
        comment_posts = paginator.page(page)

    except PageNotAnInteger:
        comment_posts = paginator.page(1)

    except EmptyPage:
        comment_posts = paginator.page(paginator.num_pages)
    
    if request.POST:
        _ticket.delete()
        return redirect('tickets')

    context = {
        'ticket': _ticket,
        'ticket_comments': ticket_comments,
        'page': page,
        'comment_posts': comment_posts
    }

    return render(request, "ticket/ticket_detail.html", context)


@login_required
def edit_ticket(request, pk):
    ticket = Ticket.objects.get(pk=pk)
    form = TicketForm(request.user, request.POST or None, instance=ticket)
    
    if form.is_valid():
        form.save()
        return redirect("tickets")

    context = {
        'edit_ticket_form': form
    }

    return render(request, "ticket/edit_ticket.html", context)


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

    return render(request, "project/new_project.html", context)


@login_required
def project_detail(request, pk):
    project = Project.objects.get(pk=pk)
    project_tickets = Ticket.objects.filter(project=project.id)
        
    context = {
        'project': project,
        'project_tickets': project_tickets
    }

    return render(request, "project/project_detail.html", context)


@login_required
def edit_project(request, pk):
    project = Project.objects.get(pk=pk)
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect("projects")

    context = {
        'edit_project_form': form
    }

    return render(request, "project/edit_project.html", context)


@login_required
def admin_user_view(request):
    user_list = UserProfile.objects.all().order_by('last_name')
    user_roles_dict = {}

    for user in user_list:
        user_roles_dict[user.id] = list(user.roles)
  
    context = {
        'user_list': user_list,
        'user_roles_dict': user_roles_dict,
    }

    return render(request, "user/roles.html", context)


@login_required
def edit_roles(request, pk):
    user = UserProfile.objects.get(pk=pk)
    role_form = UserRolesForm(request.POST or None, instance=user)

    if role_form.is_valid():
        role_form.save()
        return redirect('admin_user_view')

    context = {
        'user': user,
        'role_form': role_form
    }

    return render(request, 'user/edit_roles.html', context)


@login_required
def archived_projects(request):
    project_list = Project.objects.filter(archived=True).order_by('title')

    context = {
        'project_list': project_list
    }

    return render(request, 'project/archived_projects.html', context)


@login_required
def archive_project(request, pk):
    project = Project.objects.get(pk=pk)

    if request.POST:
        project.archived = True
        project.save()
        return redirect('projects')
    
    context = {
        'project': project
    }

    return render(request, 'project/archive_project.html', context)


@login_required
def assign_users(request, pk):
    project = Project.objects.get(pk=pk)
    project_users = project.users.all()
    all_users = UserProfile.objects.exclude(id__in=project.users.all())
    remove_project_users_form = AddProjectUsersForm(project_users, request.POST or None)
    add_project_users_form = RemoveProjectUsersForm(all_users, request.POST or None)

    if request.method == 'POST':
        if request.POST.get("assigned"):
            selected_users = request.POST.getlist("assigned")
            users_to_remove = UserProfile.objects.filter(id__in=selected_users)
            if remove_project_users_form.is_valid():
                for user in users_to_remove:
                    project.users.remove(user)
            
        elif request.POST.get("all_users"):
            selected_users = request.POST.getlist("all_users")
            users_to_add = UserProfile.objects.filter(id__in=selected_users)
            if add_project_users_form.is_valid():
                for user in users_to_add:
                    project.users.add(user)
        
    context = {
        'remove_project_users_form': remove_project_users_form,
        'add_project_users_form': add_project_users_form,
        'project': project
    }

    return render(request, 'user/assign_project_users.html', context)


@login_required
def assign_ticket(request, pk):
    ticket = Ticket.objects.get(pk=pk)
    assign_ticket_form = AssignTicketUserForm(request.user, ticket, request.POST or None, instance=ticket)

    if assign_ticket_form.is_valid():
        assign_ticket_form.save()
        return redirect("/tickets/detail/" + str(ticket.id))

    context = {
        'ticket': ticket,
        'assign_ticket_form': assign_ticket_form
    }

    return render(request, 'ticket/assign_ticket.html', context)


@login_required
def new_comment(request, pk):
    ticket = Ticket.objects.get(pk=pk)
    new_comment_form = CommentForm(request.POST)

    if new_comment_form.is_valid():
        comment = new_comment_form.save(commit=False)
        comment.user = request.user
        comment.ticket = ticket
        comment.save()
        return redirect("/tickets/detail/" + str(ticket.id))

    context = {
        'new_comment_form': new_comment_form,
        'ticket': ticket
    }

    return render(request, 'ticket/new_comment.html', context)


@login_required
def delete_comment(request, pk):
    comment = Comment.objects.get(pk=pk)

    if request.POST:
        comment.delete()
        return redirect("/tickets/detail/" + str(comment.ticket.id))

    context = {
        'comment': comment,
    }

    return render(request, 'ticket/delete_comment.html', context)


@login_required
def edit_comment(request, pk):
    comment = Comment.objects.get(pk=pk)
    edit_comment_form = CommentForm(request.POST or None, instance=comment)

    if edit_comment_form.is_valid():
        edit_comment_form.save()
        return redirect("/tickets/detail/" + str(comment.ticket.id))

    context = {
        'comment': comment,
        'edit_comment_form': edit_comment_form
    }

    return render(request, 'ticket/edit_comment.html', context)


def ticket_history(request, pk):
    ticket = Ticket.objects.get(pk=pk)
    audit_trail = TicketAuditTrail.objects.filter(ticket=ticket.id).order_by('-date_added')
    first_audit = TicketAuditTrail.objects.filter(ticket=ticket.id).earliest('date_added')
    paginator = Paginator(audit_trail, 5)
    page = request.GET.get('page')

    try:
        ticket_audits = paginator.page(page)
    except PageNotAnInteger:
        ticket_audits = paginator.page(1)
    except EmptyPage:
        ticket_audits = paginator.page(paginator.num_pages)

    context = {
        'ticket': ticket,
        'ticket_audits': ticket_audits,
        'page': page,
        'audit_trail': audit_trail,
        'first_audit': first_audit
    }
    return render(request, 'ticket/ticket_history.html', context)


def manage_profile(request):
    context = {
        'my_user': request.user
    }

    return render(request, 'user/profile.html', context)