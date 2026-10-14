from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    path('', views.room_list_view, name='room_list'),
    path('available/', views.available_rooms_view, name='available_rooms'),
    path('<int:room_id>/', views.room_detail_view, name='room_detail'),
    path('request/<int:room_id>/', views.request_assignment_view, name='request_assignment'),
]