'''
Authorization shared by the custom administration area
'''

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils.cache import add_never_cache_headers


def staff_required(view):
    @login_required(login_url='login')
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_active or not request.user.is_staff:
            raise PermissionDenied('Administrator access is required.')

        response = view(request, *args, **kwargs)

        add_never_cache_headers(response)

        return response

    return wrapped
