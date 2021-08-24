# webtech URL Configuration
# This is the top-level URL router

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('movietrack.urls')),
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls, name='admin'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# the above static function is needed to make it possible to serve user-submitted files
