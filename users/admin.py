from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from management.models import Violation
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
    actions = ['activate_users', 'mark_as_fully_paid', 'mark_as_not_paid']

    def activate_users(self, request, queryset):
        """Admin action to activate selected user accounts."""
        queryset.update(is_active=True)
        self.message_user(request, f"Successfully activated {queryset.count()} user(s).")
    activate_users.short_description = "Activate selected users"

    def mark_as_fully_paid(self, request, queryset):
        """Admin action to mark selected users as fully paid."""
        updated_count = queryset.update(payment_status='fully_paid')
        self.message_user(request, f"Successfully marked {updated_count} user(s) as Fully Paid.")
    mark_as_fully_paid.short_description = "Mark selected as Fully Paid"

    def mark_as_not_paid(self, request, queryset):
        """Admin action to mark selected users as not paid."""
        updated_count = queryset.update(payment_status='not_paid')
        self.message_user(request, f"Successfully marked {updated_count} user(s) as Not Paid.")
    mark_as_not_paid.short_description = "Mark selected as Not Paid"

    # --- List View ---
    list_display = ('student_id', 'full_name', 'role', 'payment_status', 'is_active_icon')
    list_filter = ('year_level', 'payment_status', 'is_active', 'role')
    search_fields = ('student_id', 'first_name', 'last_name')
    ordering = ('student_id',)
    list_editable = ('payment_status',) # is_active is now managed by the icon/action

    def is_active_icon(self, obj):
        return obj.is_active
    is_active_icon.boolean = True
    is_active_icon.short_description = 'Active'


    # --- Detail View ---
    fieldsets = (
        ('Identity', {'fields': ('student_id', 'first_name', 'middle_name', 'last_name')}),
        ('Academic', {'fields': ('course', 'year_level')}),
        ('Contact', {'fields': ('email', 'contact_number')}),
        ('Financial', {'fields': ('payment_status',)}),
        ('Dormitory Info', {'fields': ('role', 'assigned_room', 'cleaning_group')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Inlines allow editing related models on the same page
    inlines = [ViolationInline]

    # --- Add User Form ---
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('student_id', 'first_name', 'middle_name', 'last_name', 'email', 'role', 'assigned_room', 'cleaning_group'),
        }),
    )

# We don't need to register Violation separately anymore since it's an inline
# admin.site.register(Violation)