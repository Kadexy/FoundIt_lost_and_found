"""
WSGI config for foundIt project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foundIt.settings')

application = get_wsgi_application()

# Extra safety: serve static files in production even if middleware-based
# WhiteNoise config is bypassed or collectstatic behavior differs on the host.
try:
    from django.conf import settings
    from whitenoise import WhiteNoise

    application = WhiteNoise(application, root=settings.STATIC_ROOT, prefix='static/')
    for static_dir in getattr(settings, 'STATICFILES_DIRS', []):
        application.add_files(static_dir, prefix='static/')
except Exception:
    # If WhiteNoise isn't installed or settings aren't ready, fall back to Django.
    pass
