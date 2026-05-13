from django.middleware.csrf import CsrfViewMiddleware


class ApiAwareCsrfViewMiddleware(CsrfViewMiddleware):
    """
    Keep CSRF protection for template/admin views while allowing JWT-auth API
    requests under /api/ that do not use session cookies.
    """

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if request.path.startswith('/api/'):
            return None
        return super().process_view(request, callback, callback_args, callback_kwargs)
