"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from . import settings
from django.conf.urls.static import static
import os
import sys


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('storefront.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]

# Only add media URL patterns when explicitly allowed. In production this is
# normally handled by a storage service or web server but we support an
# opt-in env var DJANGO_SERVE_MEDIA to enable serving media from the app's
# filesystem (useful if you keep media in the deployed artifact or writable
# app directory). We also allow serving when DEBUG is True or when running
# the dev server.
if (
    settings.DEBUG
    or 'runserver' in sys.argv
    or os.environ.get('DJANGO_SERVE_MEDIA', 'False').lower() in ('1', 'true', 'yes')
):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
