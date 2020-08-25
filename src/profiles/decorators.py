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
        