from django.contrib import admin
from django.urls import path, include

# DormMeyt/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),  # Change 'users/' to '' 
    path('rooms/', include('rooms.urls')),
    path('schedule/', include('scheduling.urls')),
]