from django import forms
from django.contrib import admin
from .models import Announcement, CleaningGroup, CleaningSchedule
from users.models import User # Import the User model

# Define an inline for the members of a cleaning group
class MemberInline(admin.StackedInline):
    model = User # Use the imported User model directly
    extra = 0
    fields = ('full_name', 'student_id')
    readonly_fields = ('full_name', 'student_id')
    verbose_name = "Member"
    verbose_name_plural = "Members"
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = '__all__'
        widgets = {
            'event_date': forms.SplitDateTimeWidget(date_format='%Y-%m-%d', time_format='%H:%M'),
        }

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    form = AnnouncementForm
    list_display = ('title', 'event_date', 'date_posted')
    list_filter = ('event_date',)
    search_fields = ('title', 'content')
    ordering = ('-date_posted',)

    # Group fields for a cleaner form layout
    fieldsets = (
        (None, {
            'fields': ('title', 'content')
        }),
        ('Scheduling (Optional)', {
            'classes': ('collapse',),
            'fields': ('event_date',),
            'description': 'Set a date and time if this announcement is for a specific event.'
        }),
    )

@admin.register(CleaningGroup)
class CleaningGroupAdmin(admin.ModelAdmin):
    """
    Customizes the admin interface for Cleaning Groups.
    - Displays the group name.
    - Shows members in a read-only inline view.
    """
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [MemberInline]

@admin.register(CleaningSchedule)
class CleaningScheduleAdmin(admin.ModelAdmin):
    """
    Customizes the admin interface for Cleaning Schedules.
    - Displays the group and its assigned day.
    - Adds filters for the day of the week and the group.
    """
    list_display = ('group', 'day_of_week')
    list_filter = ('day_of_week', 'group')