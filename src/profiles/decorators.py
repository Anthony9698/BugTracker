from functools import wraps
from django.core.exceptions import PermissionDenied
from profiles.models import UserProfile, Project, Ticket, Comment, TicketAuditTrail
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

def is_admin(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        user_roles = [role for role in request.user.roles]
        if 'Admin' in user_roles:
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
        if 'Admin' in user_roles or 'Project Manager' in user_roles:
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

        if request.user != comment.user and'Admin' not in user_roles and 'Project Manager' not in user_roles:
            raise PermissionDenied

        return function(request, pk, *args, **kwargs)
    return wrap

            