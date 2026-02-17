from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models

# --- 1. USER MANAGER ---
class UserManager(BaseUserManager):
    def create_user(self, student_id, password=None, **extra_fields):
        if not student_id:
            raise ValueError('The Student ID must be set')
        user = self.model(student_id=student_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, student_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(student_id, password, **extra_fields)

# --- 2. CUSTOM USER MODEL ---
class User(AbstractUser):
    PAYMENT_STATUS_CHOICES = [
        ('not_paid', 'Not Paid'),
        ('partially_paid', 'Partially Paid'),
        ('fully_paid', 'Fully Paid'),
    ]
    username = None 
    role = models.CharField(
        max_length=10, 
        choices=(('admin', 'Dorm Manager'), ('student', 'Student Resident')), 
        default='student'
    )
    student_id = models.CharField(max_length=20, unique=True, verbose_name="Student ID Number")
    full_name = models.CharField(max_length=255)
    age = models.IntegerField(null=True, blank=True)
    course = models.CharField(max_length=100, blank=True, null=True)
    year_level = models.IntegerField(null=True, blank=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='not_paid',
        verbose_name="Payment Status"
    )
    
    # FIX: Point to the Room model in the 'rooms' app
    assigned_room = models.ForeignKey(
        'rooms.Room', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='user_assigned_rooms' 
    )

    cleaning_group = models.ForeignKey(
        'scheduling.CleaningGroup',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members'
    )

    groups = models.ManyToManyField(Group, related_name="user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="user_permissions", blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'student_id'
    REQUIRED_FIELDS = ['full_name', 'email']

    class Meta:
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.student_id} - {self.full_name}"

# --- 3. VIOLATION MODEL ---
class Violation(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='violations')
    type_of_violation = models.CharField(max_length=255)
    description = models.TextField()
    date_committed = models.DateField()
    penalty_notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Violations"

    def __str__(self):
        return f"{self.type_of_violation} - {self.student.full_name}"