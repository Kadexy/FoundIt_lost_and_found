"""
URL configuration for foundIt project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from . import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

schema_view = get_schema_view(
   openapi.Info(
      title="Kadex foundIt Backend API",
      default_version='v1',
      description="Current Backend API for these project",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="dextemid090@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('signup/', TemplateView.as_view(template_name='signup.html'), name='signup'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('report/', TemplateView.as_view(template_name='report.html'), name='report'),
    path('profile/', TemplateView.as_view(template_name='profile.html'), name='profile'),
    path('items-lost/', TemplateView.as_view(template_name='items-lost.html'), name='items-lost'),
    path('items-found/', TemplateView.as_view(template_name='items-found.html'), name='items-found'),
    path('item-detail/', TemplateView.as_view(template_name='item-detail.html'), name='item-detail'),
    path('api/admin/', admin.site.urls),
    path('api/user/', include('users.urls')),
    path('api/items/', include('items.urls')),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # Let Django's staticfiles app serve assets in development (includes admin/ and app static).
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()

