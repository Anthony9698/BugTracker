from functools import wraps
from django.core.exceptions import PermissionDenied
from profiles.models import UserProfile, Project, Ticket, Comment
from django.http import *
from profiles.utils import get_user_tickets


def user_has_role(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        user_roles = [role for role in request.user.roles]
        if len(user_roles) > 0:
            return function(request, *args, **kwargs)
        raise PermissionDenied
    return wrap


def not_demo_user(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        submitter = UserProfile.objects.get(pk=4)
        developer = UserProfile.objects.get(pk=3)
        project_manager = UserProfile.objects.get(pk=2)
        admin = UserProfile.objects.get(pk=1)
        demo_users = [submitter, developer, project_manager, admin]

        if request.user in demo_users:
            raise PermissionDenied
        return function(request, *args, **kwargs)
    return wrap


def is_admin(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        user_roles = [role for role in request.user.roles]
        if 'Admin' in user_roles or request.user.is_admin:
            return function(request, *args, **kwargs)
        raise PermissionDenied
    return wrap


def is_project_manager(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        user_roles = [role for role in request.user.roles]
        if 'Project Manager' in user_roles:
            return function(request, *args, **kwargs)
        raise PermissionDenied
    return wrap


def is_admin_or_manager(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        user_roles = [role for role in request.user.roles]
        if 'Admin' in user_roles or request.user.is_admin or 'Project Manager' in user_roles:
            return function(request, *args, **kwargs)
        raise PermissionDenied
    return wrap


def ticket_exists_viewable(function):
    @wraps(function)
    def wrap(request, pk, *args, **kwargs):
        user_roles = [role for role in request.user.roles]

        try:
            ticket = Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            raise Http404

        if ticket not in get_user_tickets(request, user_roles):
            raise PermissionDenied
        return function(request, pk, *args, **kwargs)
    return wrap


def project_exists_viewable(function):
    @wraps(function)
    def wrap(request, pk, *args, **kwargs):
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            raise Http404

        if request.user not in project.users.all():
            raise PermissionDenied
        return function(request, pk, *args, **kwargs)
    return wrap


def comment_exists_editable(function):
    @wraps(function)
    def wrap(request, pk, *args, **kwargs):
        user_roles = [role for role in request.user.roles]
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            raise Http404

        if request.user != comment.user and'Admin' not in user_roles and not request.user.is_admin and 'Project Manager' not in user_roles:
            raise PermissionDenied

        return function(request, pk, *args, **kwargs)
    return wrap

            