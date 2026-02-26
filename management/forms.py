from django import forms
from .models import Announcement, Violation
from django.contrib.auth import get_user_model

User = get_user_model()

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'date_posted']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter announcement title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter announcement content'}),
            'date_posted': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default value for date_posted to current datetime
        from django.utils import timezone
        from datetime import datetime
        if not self.instance.pk:  # Only for new instances
            now = timezone.now()
            # Format for datetime-local input: YYYY-MM-DDTHH:MM
            self.fields['date_posted'].initial = now.strftime('%Y-%m-%dT%H:%M')

class ViolationForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=False),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Violation
        fields = ['student', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class PaymentStatusForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['payment_status']
        widgets = {
            'payment_status': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        }