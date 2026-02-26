from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .forms import RegistrationForm, UserProfileForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

# Import models from other apps
from management.models import Announcement as ManagementAnnouncement, Violation
from scheduling.models import Announcement
from rooms.models import Room, Occupancy

User = get_user_model()

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
            return redirect('login')
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
                            return redirect('dashboard')
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
    return redirect('login')

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

    # 1. FETCH ROOM FROM OCCUPANCY (Source of Truth)
    try:
        occupancy = Occupancy.objects.get(student=current_user)
        display_room = occupancy.room
    except Occupancy.DoesNotExist:
        display_room = None

    # 2. FETCH ROOMMATES
    if display_room:
        roommate_ids = Occupancy.objects.filter(room=display_room).exclude(student=current_user).values_list('student_id', flat=True)
        display_roommates = User.objects.filter(id__in=roommate_ids)

    # 3. FETCH ANNOUNCEMENTS (from the management app)
    all_announcements = ManagementAnnouncement.objects.all().order_by('-date_posted')

    # 4. FETCH VIOLATIONS for the current user
    user_violations = Violation.objects.filter(student=current_user).order_by('-date_committed')

    # 5. GET PAYMENT STATUS
    payment_status = current_user.get_payment_status_display()

    context = {
        'display_room': display_room,
        'display_roommates': display_roommates,
        'announcements': all_announcements,
        'user_violations': user_violations,
        'payment_status': payment_status,
    }
    return render(request, 'dashboard.html', context)

# --- 6. RULES VIEW ---
@login_required
def rules_view(request):
    return render(request, 'rules.html')


# --- 5. ACCOUNT SETTINGS VIEW ---
@login_required
def account_view(request):
    user = request.user
    violations = user.management_violations.all().order_by('-date_committed')

    if request.method == 'POST':
        if 'change_password' in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated!')
                return redirect('account')
            else:
                messages.error(request, 'Please correct the password change errors below.')
        
        if 'update_profile' in request.POST:
            profile_form = UserProfileForm(request.POST, request.FILES, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Your profile has been updated.')
                return redirect('account')
            else:
                messages.error(request, 'Please correct the profile update errors below.')

    password_form = PasswordChangeForm(user)
    profile_form = UserProfileForm(instance=user)
    
    return render(request, 'account.html', {
        'password_form': password_form,
        'profile_form': profile_form,
        'violations': violations
    })