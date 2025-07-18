from django.http import HttpResponseRedirect
from django.urls import reverse

class AdminRedirectMiddleware:
    """
    Redirect staff users away from front-end views to admin dashboard.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.frontend_views = {
            'login', 'signup', 'buy-sell', 'dashboard',
            'portfolio', 'settings', 'wishlist', 'profit-loss', 'timeline',
        }

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        user = getattr(request, "user", None)
        if user and user.is_authenticated and user.is_staff:
            resolver_match = request.resolver_match

            if resolver_match:
                url_name = resolver_match.view_name or resolver_match.url_name

                if url_name in self.frontend_views:
                    return HttpResponseRedirect(reverse('admin-index'))

        return None
