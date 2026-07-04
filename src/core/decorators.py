from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def staff_role_required(*allowed_roles):
    """
    Decorator to require a staff member to have a specific role.
    usage:
        @staff_role_required('admin')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required(login_url='login')

        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_staff:
                raise PermissionDenied
            if not any(role in request.user.roles for role in allowed_roles):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def staff_login_required(view_func):

    """Checks if User is any active staff member. Use general dashboard views
    usage:
    @staff_login_required
    """

    @wraps(view_func)
    @login_required(login_url='staff_login')
    def _wrapped(request, *args, **kwargs):
        staff_profile = getattr(request.user, 'staff_profile', None)
        if staff_profile is None or not staff_profile.is_active:
            raise PermissionDenied("Active Staff Only")
        return view_func(request, *args, **kwargs)
    return _wrapped