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
        if form.is_valid():
            # These are the variables the form actually creates
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Use those variables here
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
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
    # This uses the OneToOne relationship in rooms/models.py
    try:
        # We look for the Occupancy record linked to the student
        occupancy = Occupancy.objects.get(student=current_user)
        display_room = occupancy.room
    except Occupancy.DoesNotExist:
        display_room = None

    # 2. FETCH ROOMMATES
    if display_room:
        # We find everyone else whose Occupancy record links to this same room
        roommate_ids = Occupancy.objects.filter(room=display_room).exclude(student=current_user).values_list('student_id', flat=True)
        display_roommates = User.objects.filter(id__in=roommate_ids)

    # 3. FETCH ANNOUNCEMENTS (from the scheduling app)
    all_announcements = Announcement.objects.all().order_by('-date_posted')[:5]

    context = {
        'display_room': display_room,
        'display_roommates': display_roommates,
        'announcements': all_announcements,
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
    violations = user.violations.all().order_by('-date_committed')

    if request.method == 'POST':
        password_form = PasswordChangeForm(user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('account')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        password_form = PasswordChangeForm(user)
    
    return render(request, 'account.html', {
        'password_form': password_form,
        'violations': violations
    })