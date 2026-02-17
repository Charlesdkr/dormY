from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Room

@login_required
def room_list_view(request):
    """
    This view fetches all rooms and their occupants to display in the room directory.
    
    It uses `prefetch_related` to efficiently load the occupants for each room,
    which helps to reduce the number of database queries and improve performance.
    """
    rooms = Room.objects.prefetch_related('room_occupants__student').all().order_by('room_number')
    
    context = {
        'rooms': rooms
    }
    return render(request, 'rooms.html', context)