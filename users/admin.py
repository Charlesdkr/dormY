from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Violation
from .forms import CustomUserCreationForm, CustomUserChangeForm

class ViolationInline(admin.TabularInline):
    """
    Allows managing violations directly within the user's admin page.
    - Displays violations in a compact, table-like format.
    - Provides extra fields for quick editing.
    """
    model = Violation
    extra = 1  # Show one empty form for adding a new violation
    fields = ('type_of_violation', 'description', 'date_committed', 'penalty_notes')
    ordering = ('-date_committed',)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    A fully-featured admin interface for the custom User model.
    """
    # --- Use Custom Forms ---
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    # --- Actions ---
    actions = ['activate_users']

    def activate_users(self, request, queryset):
        """Admin action to activate selected user accounts."""
        queryset.update(is_active=True)
        self.message_user(request, f"Successfully activated {queryset.count()} user(s).")
    activate_users.short_description = "Activate selected users"

    # --- List View ---
    list_display = ('student_id', 'full_name', 'role', 'cleaning_group', 'payment_status', 'is_active', 'is_staff')
    list_filter = ('is_active', 'role', 'payment_status', 'assigned_room__floor', 'cleaning_group')
    search_fields = ('student_id', 'full_name', 'email')
    ordering = ('student_id',)

    # --- Detail View ---
    fieldsets = (
        (None, {'fields': ('student_id', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'email', 'age', 'course', 'year_level', 'contact_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dorm Details', {'fields': ('role', 'assigned_room', 'cleaning_group', 'payment_status')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Inlines allow editing related models on the same page
    inlines = [ViolationInline]

    # --- Add User Form ---
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('student_id', 'full_name', 'email', 'role', 'assigned_room', 'cleaning_group'),
        }),
    )

# We don't need to register Violation separately anymore since it's an inline
admin.site.register(Violation)