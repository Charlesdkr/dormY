from django.db import models
from django.utils import timezone
from django.conf import settings

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class Violation(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='management_violations')
    description = models.TextField()
    date_committed = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Violation for {self.student} on {self.date_committed.strftime('%Y-%m-%d')}"