from django.urls import path
from django.urls import path
from . import views

app_name = 'management'

urlpatterns = [
    path('dashboard/', views.management_dashboard_view, name='management_dashboard'),
    path('violations/', views.manage_violations_view, name='manage_violations'),
    path('payments/', views.manage_payments_view, name='manage_payments'),
]