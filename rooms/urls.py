from django.urls import path
from . import views

urlpatterns = [
    path('', views.room_list_view, name='room_list'),
]