from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm as BaseUserChangeForm

from .models import User, EmergencyContact
from management.models import Request


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['student_id', 'first_name', 'middle_name', 'last_name', 'email', 'course', 'year_level', 'contact_number', 'password']
        widgets = {
            'student_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2024-0001'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'course': forms.TextInput(attrs={'class': 'form-control'}),
            'year_level': forms.NumberInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        # Users can only edit these specific fields
        fields = ['profile_picture', 'email', 'contact_number']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control mb-2'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['profile_picture'].required = False


class CustomUserCreationForm(UserCreationForm):
    """A form for creating new users in the admin, with no privileges."""

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('student_id', 'first_name', 'middle_name', 'last_name', 'email')


class CustomUserChangeForm(BaseUserChangeForm):
    """A form for updating users in the admin. Includes all fields."""

    class Meta(BaseUserChangeForm.Meta):
        model = get_user_model()
        fields = '__all__'


class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        fields = ['contact_name', 'relationship', 'phone_number']
        widgets = {
            'contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'relationship': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Mother, Father, Guardian'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['request_type', 'description']
        widgets = {
            'request_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Please provide details about your request.'}),
        }