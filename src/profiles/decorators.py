from functools import wraps
from django.core.exceptions import PermissionDenied


def is_admin(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        user_roles = [role for role in request.user.roles]
        if 'Admin' in user_roles:
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
        