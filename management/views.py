from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Announcement, Violation
from .forms import AnnouncementForm, ViolationForm, PaymentStatusForm
from django.contrib.auth import get_user_model

User = get_user_model()

from django.contrib import messages

def is_staff(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def management_dashboard_view(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save()
            messages.success(request, f'Announcement "{announcement.title}" has been posted successfully.')
            return redirect('management:management_dashboard')
        else:
            messages.error(request, 'Could not post announcement. Please check the form for errors.')
    else:
        form = AnnouncementForm()

    announcements = Announcement.objects.all().order_by('-date_posted')
    context = {
        'form': form,
        'announcements': announcements,
    }
    return render(request, 'mdashboard.html', context)

@login_required
@user_passes_test(is_staff)
def manage_violations_view(request):
    if request.method == 'POST':
        form = ViolationForm(request.POST)
        if form.is_valid():
            violation = form.save()
            messages.success(request, f'Violation has been recorded for {violation.student.full_name}.')
            return redirect('management:manage_violations')
    else:
        form = ViolationForm()

    violations = Violation.objects.all().order_by('-date_committed')
    context = {
        'form': form,
        'violations': violations,
    }
    return render(request, 'manage_violations.html', context)

@login_required
@user_passes_test(is_staff)
def manage_payments_view(request):
    students = User.objects.filter(is_staff=False).order_by('last_name')
    student_forms = {student.id: PaymentStatusForm(instance=student) for student in students}

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        try:
            student = User.objects.get(id=student_id)
            form = PaymentStatusForm(request.POST, instance=student)
            if form.is_valid():
                form.save()
                student.refresh_from_db()
                messages.success(request, f"Payment status for {student.full_name} has been updated to {student.get_payment_status_display()}.")
                return redirect('management:manage_payments')
            else:
                student_forms[student.id] = form
                messages.error(request, f'Could not update for {student.full_name}. Please correct the error.')
        except User.DoesNotExist:
            messages.error(request, 'Student not found.')

    context = {
        'students_with_forms': [(student, student_forms[student.id]) for student in students],
    }
    return render(request, 'manage_payments.html', context)