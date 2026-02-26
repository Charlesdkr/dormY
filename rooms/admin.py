from django.contrib import admin
from .models import Room
from users.models import User

class ResidentInline(admin.TabularInline):
    """
    Tabular Inline for displaying residents assigned to a room.
    This allows managing residents directly from the Room detail page.
    """
    model = User
    # Fields to display in the inline table
    fields = ('student_id', 'full_name', 'course', 'year_level')
    readonly_fields = ('student_id', 'full_name', 'course', 'year_level')
    # We don't want to add new users from the room page
    extra = 0
    # Prevent deletion of users from this view
    can_delete = False
    # Link to the user's detail page
    show_change_link = True

    def get_queryset(self, request):
        """Ensure we only show assigned residents."""
        return super().get_queryset(request).filter(assigned_room__isnull=False)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Rooms, now with integrated resident management.
    """
    list_display = ('room_number', 'floor', 'status', 'capacity', 'occupant_count')
    list_filter = ('floor', 'status')
    search_fields = ('room_number',)
    ordering = ('room_number',)
    
    # Embed the resident list directly into the Room detail page
    inlines = [ResidentInline]

    def occupant_count(self, obj):
        """Calculated field to show how many people are in the room."""
        return obj.residents.count()
    occupant_count.short_description = 'Occupants'

# The separate OccupancyAdmin is now obsolete and can be removed.
# @admin.register(Occupancy)
# class OccupancyAdmin(admin.ModelAdmin):
#     ...