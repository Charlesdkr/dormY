from django.contrib import admin
from .models import Room, Occupancy

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Rooms.
    """
    list_display = ('room_number', 'floor', 'status', 'capacity')
    list_filter = ('floor', 'status')
    search_fields = ('room_number',)
    ordering = ('room_number',)

@admin.register(Occupancy)
class OccupancyAdmin(admin.ModelAdmin):
    """
    Admin interface for managing room Occupancies.
    This allows assigning a student to a room.
    """
    list_display = ('student', 'room')
    list_filter = ('room__floor',)
    search_fields = ('student__full_name', 'room__room_number')
    autocomplete_fields = ['student', 'room'] # Makes selecting easier