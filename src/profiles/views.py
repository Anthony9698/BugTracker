import os
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from profiles.forms import RegistrationForm, LoginForm, ProjectForm, TicketForm,\
    UserRolesForm, AddProjectUsersForm, RemoveProjectUsersForm, AssignTicketUserForm,\
    CommentForm, EditProfileForm, TicketAttachmentForm
from profiles.decorators import is_admin, is_project_manager, is_admin_or_manager, \
     ticket_exists_viewable, project_exists_viewable, comment_exists_editable, user_has_role, not_demo_user
from profiles.models import UserProfile, Project, Ticket, Comment, TicketAuditTrail, Attachment
from profiles.utils import get_user_tickets, send_comment_added_email
from .models import UserProfile


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
@is_admin
def admin_user_view(request):
    user_list = UserProfile.objects.all().order_by('last_name')
    user_roles_dict = {}

    for user in user_list:
        user_roles_dict[user.id] = list(user.roles)

    context = {
        'user': request.user,
        'user_roles': [role for role in request.user.roles],
        'user_list': user_list,
        'user_roles_dict': user_roles_dict,
    }

    return render(request, "user/roles.html", context)


@login_required
@is_admin
def edit_roles(request, pk):
    user = UserProfile.objects.get(pk=pk)
    role_form = UserRolesForm(request.POST or None, instance=user)
    if request.method == 'POST':
        if role_form.is_valid():
            role_form.save()
            return redirect('admin_user_view')

    context = {
        'user_roles': [role for role in request.user.roles],
        'user': user,
        'role_form': role_form
    }

    return render(request, 'user/edit_roles.html', context)


def demo(request):
    user = None
    
    if request.GET.get('Submitter') == 'Submitter':
        user = authenticate(email=os.environ.get('SUB_EMAIL'), password=os.environ.get('SUB_PASSWORD'))

    elif request.GET.get("Developer") == 'Developer':
        user = authenticate(email=os.environ.get('DEV_EMAIL'), password=os.environ.get('DEV_PASSWORD'))

    elif request.GET.get("Project Manager") == 'Project Manager':
        user = authenticate(email=os.environ.get('PROJ_EMAIL'), password=os.environ.get('PROJ_PASSWORD'))

    elif request.GET.get("Admin") == 'Admin':
        user = authenticate(email=os.environ.get('ADMIN_EMAIL'), password=os.environ.get('ADMIN_PASSWORD'))

    if user:
        login(request, user)
        return redirect('dashboard')

    return render(request, 'user/demo.html')


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
def logout_user(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("login")


@login_required
def dashboard(request):
    user_roles = [role for role in request.user.roles]
    user_projects = Project.objects.filter(Q(users__id=request.user.id) & Q(archived=False)).order_by('-date_added')
    user_tickets = list(get_user_tickets(request, user_roles))[:5]
    project_paginator = Paginator(user_projects, 4)
    page = request.GET.get('page')

    try:
        project_list = project_paginator.page(page)

    except PageNotAnInteger:
        project_list = project_paginator.page(1)

    except EmptyPage:
        project_list = project_paginator.page(project_paginator.num_pages)

    project_tickets_dict = {}
    critical_tickets_dict = {}
    resolved_tickets_dict = {}
    for proj in project_list:
        project_tickets = get_user_tickets(request, user_roles)\
                           .filter(project=proj.id).count()
        critical_tickets = get_user_tickets(request, user_roles)\
                           .filter(Q(project=proj.id) & Q(priority__exact='Critical')).count()
        resolved_tickets = get_user_tickets(request, user_roles)\
                           .filter(Q(project=proj.id) & Q(status__exact='Resolved')).count()
        project_tickets_dict[proj.id] = project_tickets
        critical_tickets_dict[proj.id] = critical_tickets
        resolved_tickets_dict[proj.id] = resolved_tickets

    context = {
        'user': request.user,
        'user_roles': user_roles,
        'user_tickets': user_tickets,
        'user_projects': user_projects,
        'project_list': project_list,
        'project_tickets_dict': project_tickets_dict,
        'critical_tickets_dict': critical_tickets_dict,
        'resolved_tickets_dict': resolved_tickets_dict
    }

    return render(request, 'dashboard.html', context)


@login_required
def tickets(request):
    user_roles = [role for role in request.user.roles]
    context = {
        'user': request.user,
        'user_roles': user_roles,
        'user_tickets': get_user_tickets(request, user_roles)
    }

    return render(request, 'ticket/tickets.html', context)


@login_required
@user_has_role
def new_ticket(request):
    proj = request.GET.get('project')
    if request.method == 'POST':
        form = TicketForm(request.user, request.POST, instance=None)

        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.owner = request.user
            ticket.save()
            return redirect("tickets")

    elif proj:
        form = TicketForm(request.user, initial={'project': proj})

    else:
        form = TicketForm(request.user)

    context = {
        'user': request.user,
        'user_roles': [role for role in request.user.roles],
        'new_ticket_form': form
    }

    return render(request, "ticket/new_ticket.html", context)


@login_required
@ticket_exists_viewable
def ticket_detail(request, pk):
    ticket = Ticket.objects.get(pk=pk)
    ticket_comments = Comment.objects.filter(ticket=ticket.id).order_by('-date_posted')
    paginator = Paginator(ticket_comments, 2)
    page = request.GET.get('page')
    
    try:
        comment_posts = paginator.page(page)

    except PageNotAnInteger:
        comment_posts = paginator.page(1)

    except EmptyPage:
        comment_posts = paginator.page(paginator.num_pages)

    context = {
        'user': request.user,
        'user_roles': [role for role in request.user.roles],
        'ticket': ticket,
        'ticket_comments': ticket_comments,
        'ticket_attachments': ticket.attachments.all(),
        'page': page,
        'comment_posts': comment_posts
    }

    return render(request, "ticket/ticket_detail.html", context)


@login_required
@ticket_exists_viewable
def edit_ticket(request, pk):
    user_roles = [role for role in request.user.roles]
    ticket = Ticket.objects.get(pk=pk)
    form = TicketForm(request.user, request.POST or None, instance=ticket)

    if form.is_valid():
        form.save()
        return redirect("/tickets/detail/" + str(ticket.id))

    context = {
        'user': request.user,
        'user_roles': user_roles,
        'edit_ticket_form': form
    }

    return render(request, "ticket/edit_ticket.html", context)


@login_required
@is_project_manager
def assign_ticket(request, pk):
    ticket = Ticket.objects.get(pk=pk)
    assign_ticket_form = AssignTicketUserForm(request.user, ticket, request.POST or None, instance=ticket)

    if assign_ticket_form.is_valid():
        assign_ticket_form.save()
        return redirect("/tickets/detail/" + str(ticket.id))

    context = {
        'user': request.user,
        'user_roles': [role for role in request.user.roles],
        'ticket': ticket,
        'assign_ticket_form': assign_ticket_form
    }

    return render(request, 'ticket/assign_ticket.html', context)


@login_required
def new_comment(request, pk):
    ticket = Ticket.objects.get(pk=pk)
    if request.method == 'POST':
        new_comment_form = CommentForm(request.POST)

        if new_comment_form.is_valid():
            comment = new_comment_form.save(commit=False)
            comment.user = request.user
            comment.ticket = ticket
            comment.save()
            return redirect("/tickets/detail/" + str(ticket.id))
    else:
        new_comment_form = CommentForm()

    context = {
        'user': request.user,
        'user_roles': [role for role in request.user.roles],
        'new_comment_form': new_comment_form,
        'ticket': ticket
    }

    return render(request, 'ticket/new_comment.html', context)


@login_required
@comment_exists_editable
def delete_comment(request, pk):
    comment = Comment.objects.get(pk=pk)

    if request.POST:
        comment.delete()
        return redirect("/tickets/detail/" + str(comment.ticket.id))

    context = {
        'user': request.user,
        'user_roles': [role for role in request.user.roles],
        'comment': comment,
    }

    return render(request, 'ticket/delete_comment.html', context)


@login_required
@comment_exists_editable
def edit_comment(request, pk):
    comment = Comment.objects.get(pk=pk)
    edit_comment_form = CommentForm(request.POST or None, instance=comment)

    if edit_comment_form.is_valid():
        edit_comment_form.save()
        return redirect("/tickets/detail/" + str(comment.ticket.id))

    context = {
        'user': request.user,
        'user_roles': [role for role in request.user.roles],
        'comment': comment,
        'edit_comment_form': edit_comment_form
    }

    return render(request, 'ticket/edit_comment.html', context)


@login_required
@ticket_exists_viewable
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
        'user': request.user,
        'user_roles': [role for role in request.user.roles],
        'ticket': ticket,
        'ticket_audits': ticket_audits,
        'page': page,
        'audit_trail': audit_trail,
        'first_audit': first_audit
    }
    
    return render(request, 'ticket/ticket_history.html', context)


@login_required
def projects(request):
    user_roles = [role for role in request.user.roles]
    # display all unarchived projects here if you are admin
    if 'Admin' in user_roles or request.user.is_admin:
        user_projects = Project.objects.filter(archived=False)

    else:
        user_projects = Project.objects.filter(Q(users__id=request.user.id) & Q(archived=False))

    context = {
        'user': request.user,
        'user_roles': user_roles,
        'user_projects': user_projects
    }

    return render(request, 'project/projects.html', context)


@login_required
@is_admin_or_manager
def new_project(request):
    if request.method == 'POST':
        new_project_form = ProjectForm(request.POST)
        if new_project_form.is_valid():
            project = new_project_form.save()
            project.users.add(request.user)
            return redirect("projects")
    else:
        new_project_form = ProjectForm()

    context = {
        'user': request.user,
        'user_roles': [role for role in request.user.roles],
        'new_project_form': new_project_form
    }

    return render(request, "project/new_project.html", context)


@login_required
@project_exists_viewable
def project_detail(request, pk):
    user_roles = [role for role in request.user.roles]
    project = Project.objects.get(pk=pk)

    context = {
        'user': request.user,
        'user_roles': user_roles,
        'project': project,
        'project_tickets': get_user_tickets(request, user_roles).filter(project=project.id)
    }

    return render(request, "project/project_detail.html", context)


@login_required
@is_admin_or_manager
def edit_project(request, pk):
    project = Project.objects.get(pk=pk)
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect("projects")

    context = {
        'user': request.user,
        'user_roles': [role for role in request.user.roles],
        'edit_project_form': form
    }

    return render(request, "project/edit_project.html", context)


@login_required
@is_admin_or_manager
def archived_projects(request):
    project_list = Project.objects.filter(archived=True).order_by('title')

    context = {
        'user': request.user,
        'user_roles': [role for role in request.user.roles],
        'project_list': project_list
    }

    return render(request, 'project/archived_projects.html', context)


@login_required
@is_admin_or_manager
def archive_project(request, pk):
    project = Project.objects.get(pk=pk)

    if request.POST:
        project.archived = True
        project.save()
        return redirect('projects')

    context = {
        'user': request.user,
        'user_roles': [role for role in request.user.roles],
        'project': project
    }

    return render(request, 'project/archive_project.html', context)


@login_required
@is_admin_or_manager
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
        'user': request.user,
        'user_roles': [role for role in request.user.roles],
        'remove_project_users_form': remove_project_users_form,
        'add_project_users_form': add_project_users_form,
        'project': project
    }

    return render(request, 'user/assign_project_users.html', context)


@login_required
@is_project_manager
def assign_ticket(request, pk):
    ticket = Ticket.objects.get(pk=pk)
    assign_ticket_form = AssignTicketUserForm(request.user, ticket, request.POST or None, instance=ticket)

    if assign_ticket_form.is_valid():
        ticket = assign_ticket_form.save(commit=False)
        ticket.status = 'Waiting for support'
        ticket.save()
        
        return redirect("confirm_assignment")

    context = {
        'user': request.user,
        'user_roles': [role for role in request.user.roles],
        'ticket': ticket,
        'assign_ticket_form': assign_ticket_form
    }

    return render(request, 'ticket/assign_ticket.html', context)


@login_required
def confirm_assignment(request):
    return render(request, 'ticket/confirm_assignment.html')


@login_required
@ticket_exists_viewable
def add_attachment(request, pk):
    context = {}
    ticket = Ticket.objects.get(pk=pk)

    if request.method == 'POST':
        form = TicketAttachmentForm(request.POST, request.FILES)

        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.uploader = request.user
            attachment.save()
            ticket.attachments.add(attachment)
            return redirect("/tickets/detail/" + str(ticket.id))
    else:
        form = TicketAttachmentForm() 

    context = {
        'ticket': ticket,
        'form': form
    }

    return render(request, "ticket/add_attachment.html", context)
    

@login_required
def new_comment(request, pk):
    ticket = Ticket.objects.get(pk=pk)
    if request.method == 'POST':
        new_comment_form = CommentForm(request.POST)

        if new_comment_form.is_valid():
            comment = new_comment_form.save(commit=False)
            comment.user = request.user
            comment.ticket = ticket
            comment.save()
            
            if comment.user is not comment.ticket.assigned_user:
                send_comment_added_email(comment.ticket.assigned_user, comment.ticket)

            return redirect("/tickets/detail/" + str(ticket.id))
    else:
        new_comment_form = CommentForm()

    context = {
        'user': request.user,
        'user_roles': [role for role in request.user.roles],
        'new_comment_form': new_comment_form,
        'ticket': ticket
    }

    return render(request, 'ticket/new_comment.html', context)


@login_required
@comment_exists_editable
def delete_comment(request, pk):
    comment = Comment.objects.get(pk=pk)

    if request.POST:
        comment.delete()
        return redirect("/tickets/detail/" + str(comment.ticket.id))

    context = {
        'user': request.user,
        'user_roles': [role for role in request.user.roles],
        'comment': comment,
    }

    return render(request, 'ticket/delete_comment.html', context)


@login_required
@comment_exists_editable
def edit_comment(request, pk):
    comment = Comment.objects.get(pk=pk)
    edit_comment_form = CommentForm(request.POST or None, instance=comment)

    if edit_comment_form.is_valid():
        edit_comment_form.save()
        return redirect("/tickets/detail/" + str(comment.ticket.id))

    context = {
        'user': request.user,
        'user_roles': [role for role in request.user.roles],
        'comment': comment,
        'edit_comment_form': edit_comment_form
    }

    return render(request, 'ticket/edit_comment.html', context)


@login_required
@ticket_exists_viewable
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
        'user': request.user,
        'user_roles': [role for role in request.user.roles],
        'ticket': ticket,
        'ticket_audits': ticket_audits,
        'page': page,
        'audit_trail': audit_trail,
        'first_audit': first_audit
    }
    return render(request, 'ticket/ticket_history.html', context)


@login_required
def manage_profile(request, *args, **kwargs):
    context = {
        'user': request.user,
        'user_roles': [role for role in request.user.roles],
        'message': request.GET.get('message')
    }

    return render(request, 'user/profile.html', context)


@login_required
@not_demo_user
def edit_profile(request):
    my_profile_form = EditProfileForm(request.POST or None, instance=request.user)

    if my_profile_form.is_valid():
        my_profile_form.save()
        return redirect('manage_profile')

    context = {
        'user': request.user,
        'user_roles': [role for role in request.user.roles],
        'my_profile_form': my_profile_form
    }

    return render(request, 'user/edit_profile.html', context)


@login_required
@not_demo_user
def change_password(request):
    if request.method == 'POST':
        password_change_form = PasswordChangeForm(request.user, request.POST)

        if password_change_form.is_valid():
            user = password_change_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            # return redirect('manage_profile')
            return redirect('{}?message=password-change-success'.format(reverse('manage_profile')))
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        password_change_form = PasswordChangeForm(request.user)

    context = {
        'user': request.user,
        'user_roles': [role for role in request.user.roles],
        'change_password_form': password_change_form
    }

    return render(request, 'user/change_password.html', context)

@login_required
def about(request):
    return render(request, 'about.html')
