from django.db import models
from django.utils import timezone
from django.conf import settings

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    event_date = models.DateTimeField(null=True, blank=True)
    date_posted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class Violation(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='management_violations')
    description = models.TextField()
    date_committed = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Violation for {self.student} on {self.date_committed.strftime('%Y-%m-%d')}"

class CleaningGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='cleaning_groups', limit_choices_to={'is_staff': False})

    def __str__(self):
        return self.name

class CleaningSchedule(models.Model):
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    group = models.ForeignKey(CleaningGroup, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    task = models.TextField()

    def __str__(self):
        return f"{self.group.name} - {self.day_of_week}"

class Request(models.Model):
    REQUEST_TYPES = (
        ('maintenance', 'Maintenance'),
        ('stay_out', 'Stay Out Overnight'),
        ('other', 'Other'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    )

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requests')
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    date_submitted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Request from {self.student} ({self.get_request_type_display()})"