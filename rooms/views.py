from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import AssignmentRequest, Occupancy, Room

def room_list_view(request):
    """
    Fetches rooms and determines if the user can make an assignment request.
    Made public for guests to view available rooms.
    """
    rooms = Room.objects.prefetch_related('residents').all().order_by('room_number')

    # Only compute request-related info if user is authenticated
    pending_request = None
    can_make_request = False
    current_user_room = None

    if request.user.is_authenticated:
        pending_request = AssignmentRequest.objects.filter(student=request.user, status='pending').first()
        can_make_request = not pending_request
        if hasattr(request.user, 'room_assignment') and request.user.room_assignment:
            current_user_room = request.user.room_assignment.room

    context = {
        'rooms': rooms,
        'can_make_request': can_make_request,
        'pending_request_room': pending_request.room if pending_request else None,
        'current_user_room': current_user_room,
    }
    return render(request, 'rooms.html', context)


def room_detail_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    context = {
        'room': room,
    }
    return render(request, 'room_detail.html', context)


def available_rooms_view(request):
    rooms = Room.objects.prefetch_related('residents').filter(status='available').order_by('room_number')
    context = {
        'rooms': rooms,
    }
    return render(request, 'available_rooms.html', context)


@login_required
def request_assignment_view(request, room_id):
    room_to_request = get_object_or_404(Room, id=room_id)
    student = request.user

    # More reliable check for the student's current room by querying the DB directly.
    current_occupancy = Occupancy.objects.filter(student=student).first()
    current_room = current_occupancy.room if current_occupancy else None

    # Prevent student from requesting the same room they are already in.
    if current_room and current_room == room_to_request:
        messages.error(request, f"You are already in Room {room_to_request.room_number}.")
        return redirect('rooms:room_list')

    # Check for an existing pending request for any room.
    if AssignmentRequest.objects.filter(student=student, status='pending').exists():
        messages.warning(request, "You already have a pending request. Please wait for it to be processed.")
        return redirect('rooms:room_list')

    # Check if the room is available.
    if room_to_request.status != 'available':
        messages.error(request, f"Room {room_to_request.room_number} is not available for requests.")
        return redirect('rooms:room_list')

    # Use get_or_create to safely handle requests. This prevents IntegrityError
    # by reusing existing requests (e.g., a rejected one) instead of creating duplicates.
    assignment_request, created = AssignmentRequest.objects.get_or_create(
        student=student, 
        room=room_to_request,
        defaults={'status': 'pending'} # This is used only if a new object is created
    )

    if not created:
        # If the request already existed, we update its status to re-submit it.
        assignment_request.status = 'pending'
        assignment_request.save()
        messages.info(request, f"Your request for Room {room_to_request.room_number} has been re-submitted.")
    else:
        # A new request was created.
        messages.success(request, f"Your request to join Room {room_to_request.room_number} has been submitted.")
    
    return redirect('rooms:room_list')