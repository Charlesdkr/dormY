from django import forms
from .models import Room

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'floor', 'capacity', 'photo', 'description']
        widgets = {
            'room_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 101, 202A'}),
            'floor': forms.Select(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 4'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/jpeg,image/jpg,image/png'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Room features, facilities, bed capacity, amenities, etc.'}),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            if photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image size should not exceed 5MB.')
            content_type = getattr(photo, 'content_type', None)
            if content_type and content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
                raise forms.ValidationError('Only JPG, JPEG, and PNG images are allowed.')
        return photo