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
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)
    course = models.CharField(max_length=100, blank=True, null=True)
    year_level = models.IntegerField(null=True, blank=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True, default='profile_pics/default.jpg')
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
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    class Meta:
        verbose_name_plural = "Users"

    @property
    def full_name(self):
        """Returns the user's full name."""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.student_id} - {self.full_name}"