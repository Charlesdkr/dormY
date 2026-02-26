from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
from datetime import date, timedelta
from django.utils import timezone
from .models import CleaningSchedule
from management.models import Announcement as ManagementAnnouncement

def get_next_weekday(weekday):
    """
    Calculates the date of the next occurrence of a given weekday.
    """
    today = date.today()
    days_ahead = weekday - today.weekday()
    if days_ahead <= 0:  # Target day has already passed this week
        days_ahead += 7
    return today + timedelta(days=days_ahead)

@login_required
def schedule_view(request):
    """
    This view prepares the data for the schedule page, including cleaning schedules
    and announcements, and formats it for FullCalendar.
    """
    all_schedules = CleaningSchedule.objects.select_related('group').prefetch_related('group__members').all()
    
    # Fetch all announcements from the management app
    all_announcements = ManagementAnnouncement.objects.order_by('-date_posted')
    
    context = {
        'all_schedules': all_schedules,
        'all_announcements': all_announcements,
    }
    
    return render(request, 'schedule.html', context)