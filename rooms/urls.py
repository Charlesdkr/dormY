from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    path('', views.room_list_view, name='room_list'),
    path('request/<int:room_id>/', views.request_assignment_view, name='request_assignment'),
]