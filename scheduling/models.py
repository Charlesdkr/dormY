from django.db import models
from django.conf import settings

# 1. Announcements Table
class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    event_date = models.DateTimeField(null=True, blank=True, help_text="Optional: If this is an event, set the date and time.")

    def __str__(self):
        return self.title

# 2. Cleaning Group Table
class CleaningGroup(models.Model):
    name = models.CharField(max_length=50, unique=True) # e.g., "Group A"
    
    def __str__(self):
        return self.name

# 3. Weekly Schedule Table
class CleaningSchedule(models.Model):
    DAY_CHOICES = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]
    group = models.ForeignKey(CleaningGroup, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=3, choices=DAY_CHOICES)
    
    def __str__(self):
        return f"{self.group.name} - {self.day_of_week}"