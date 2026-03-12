from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, UserProfileForm, EmergencyContactForm, RequestForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

# Import models from other apps
from management.models import Announcement as ManagementAnnouncement, Violation, CleaningSchedule
from scheduling.models import Announcement
from rooms.models import Room, Occupancy

User = get_user_model()

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def toggle_resident_status(request, user_id):
    if request.method == 'POST':
        resident = get_object_or_404(User, id=user_id)
        resident.is_active = not resident.is_active
        resident.save()
        messages.success(request, f"{resident.full_name}'s account has been {'activated' if resident.is_active else 'deactivated'}.")
    return redirect('management:manage_residents')

# --- 1. REGISTRATION VIEW ---
def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False  # Admin approval required
            user.save()
            messages.success(request, "Registration successful! Please wait for admin approval.")
            return redirect('users:login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

# --- 2. LOGIN VIEW ---
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        role = request.POST.get('role')

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_active:
                    # Role-based redirection
                    if role == 'master':
                        if user.is_staff:
                            login(request, user)
                            return redirect('management:management_dashboard') # New dashboard for dorm master
                        else:
                            messages.error(request, "You do not have permission to log in as a Dorm Master.")
                    else: # Default to student login
                        if user.is_staff:
                            messages.error(request, "Staff members cannot log in as students.")
                        else:
                            login(request, user)
                            return redirect('users:dashboard')
                else:
                    messages.error(request, "Your account is not active.")
            else:
                messages.error(request, "Invalid credentials.")
        else:
            messages.error(request, "Invalid credentials or account not yet active.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# --- 3. LOGOUT VIEW ---
def logout_view(request):
    logout(request)
    messages.info(request, "You have logged out.")
    return redirect('users:login')

# --- 4. DASHBOARD VIEW ---
from rooms.models import Occupancy # Source of Truth for Rooms
from scheduling.models import Announcement # Source of Truth for News
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def dashboard_view(request):
    current_user = request.user
    display_room = None
    display_roommates = []

    if request.method == 'POST':
        request_form = RequestForm(request.POST)
        if request_form.is_valid():
            new_request = request_form.save(commit=False)
            new_request.student = current_user
            new_request.save()
            messages.success(request, "Your request has been submitted successfully.")
            return redirect('users:dashboard')
    else:
        request_form = RequestForm()

    # 1. FETCH ROOM using the relationship on the user model
    if hasattr(current_user, 'room_assignment') and current_user.room_assignment:
        display_room = current_user.room_assignment.room
    else:
        display_room = None

    # 2. FETCH ROOMMATES using the relationship on the room model
    if display_room:
        display_roommates = display_room.residents.exclude(id=current_user.id)

    # 3. FETCH ANNOUNCEMENTS (from the management app)
    all_announcements = ManagementAnnouncement.objects.all().order_by('-date_posted')

    # 4. FETCH VIOLATIONS for the current user
    user_violations = Violation.objects.filter(student=current_user).order_by('-date_committed')

    # 5. GET PAYMENT STATUS
    payment_status = current_user.get_payment_status_display()

    # 6. GET USER REQUESTS
    user_requests = current_user.requests.all().order_by('-date_submitted')

    context = {
        'display_room': display_room,
        'display_roommates': display_roommates,
        'announcements': all_announcements,
        'user_violations': user_violations,
        'payment_status': payment_status,
        'request_form': request_form,
        'user_requests': user_requests,
    }
    return render(request, 'dashboard.html', context)

@login_required
def schedule_view(request):
    """
    This view prepares the data for the schedule page, including cleaning schedules
    and announcements.
    """
    schedules_by_day = {day: [] for day, _ in CleaningSchedule.DAYS_OF_WEEK}
    schedules = CleaningSchedule.objects.select_related('group').prefetch_related('group__members').all()
    
    # Group schedules in Python to preserve the pre-fetched member data
    for schedule in schedules:
        schedules_by_day[schedule.day_of_week].append(schedule)

    # Fetch all announcements from the management app
    announcements = ManagementAnnouncement.objects.order_by('-date_posted')
    
    context = {
        'schedules_by_day': schedules_by_day,
        'announcements': announcements,
        'total_schedules': schedules.count(),
    }
    
    return render(request, 'schedule.html', context)

# --- 6. RULES VIEW ---
@login_required
def rules_view(request):
    return render(request, 'rules.html')


# --- 5. ACCOUNT SETTINGS VIEW ---
@login_required
def account_view(request):
    user = request.user

    # Safely get the user's emergency contact instance, if it exists
    try:
        contact_instance = user.emergency_contact
    except ObjectDoesNotExist:
        contact_instance = None

    violations = user.management_violations.all().order_by('-date_committed')
    cleaning_group = user.cleaning_groups.prefetch_related('members').first()

    # Initialize forms for GET request or if POST fails validation
    password_form = PasswordChangeForm(user)
    profile_form = UserProfileForm(instance=user)
    emergency_contact_form = EmergencyContactForm(instance=contact_instance)

    if request.method == 'POST':
        if 'change_password' in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated!')
                return redirect('users:account')
            else:
                messages.error(request, 'Please correct the password change errors below.')

        elif 'update_profile' in request.POST:
            profile_form = UserProfileForm(request.POST, request.FILES, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Your profile has been updated.')
                return redirect('users:account')
            else:
                messages.error(request, 'Please correct the profile update errors below.')

        elif 'update_emergency_contact' in request.POST:
            emergency_contact_form = EmergencyContactForm(request.POST, instance=contact_instance)
            if emergency_contact_form.is_valid():
                contact = emergency_contact_form.save(commit=False)
                contact.user = user  # Explicitly link the user
                contact.save()
                messages.success(request, 'Your emergency contact information has been updated.')
                return redirect('users:account')
            else:
                messages.error(request, 'Please correct the emergency contact errors below.')

    return render(request, 'account.html', {
        'password_form': password_form,
        'profile_form': profile_form,
        'emergency_contact_form': emergency_contact_form,
        'violations': violations,
        'cleaning_group': cleaning_group,
    })