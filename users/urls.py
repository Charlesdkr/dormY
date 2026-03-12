from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'users'

urlpatterns = [
    path('', RedirectView.as_view(url='login/', permanent=False)),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('schedule/', views.schedule_view, name='schedule'),
    path('rules/', views.rules_view, name='rules'),
    path('account/', views.account_view, name='account'),
    path('residents/toggle-status/<int:user_id>/', views.toggle_resident_status, name='toggle_resident_status'),
]