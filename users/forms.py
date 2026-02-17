from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm as BaseUserChangeForm

from .models import User


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['student_id', 'full_name', 'email', 'course', 'year_level', 'contact_number', 'password']
        widgets = {
            'student_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2024-0001'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'course': forms.TextInput(attrs={'class': 'form-control'}),
            'year_level': forms.NumberInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'email', 'contact_number', 'course', 'year_level']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.TextInput(attrs={'class': 'form-control'}),
            'year_level': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class CustomUserCreationForm(UserCreationForm):
    """A form for creating new users in the admin, with no privileges."""

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('student_id', 'full_name', 'email')


class CustomUserChangeForm(BaseUserChangeForm):
    """A form for updating users in the admin. Includes all fields."""

    class Meta(BaseUserChangeForm.Meta):
        model = get_user_model()
        fields = '__all__'