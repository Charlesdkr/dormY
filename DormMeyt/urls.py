from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# DormMeyt/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),  # Change 'users/' to '' 
    path('rooms/', include('rooms.urls')),
    path('schedule/', include('scheduling.urls')),
    path('management/', include('management.urls', namespace='management')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)