from django.db import models
from django.conf import settings

class Room(models.Model):
    FLOOR_CHOICES = [
        (1, '1st Floor'),
        (2, '2nd Floor'),
        (3, '3rd Floor'),
    ]
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('full', 'Full'),
        ('maintenance', 'Under Maintenance'),
    ]

    room_number = models.CharField(max_length=10, unique=True)
    floor = models.IntegerField(choices=FLOOR_CHOICES, default=1)
    capacity = models.IntegerField(default=4)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return f"Room {self.room_number} - {self.get_floor_display()}"

    @property
    def is_full(self):
        return self.room_occupants.count() >= self.capacity

    def save(self, *args, **kwargs):
        # Automatically update status based on occupancy, but respect 'maintenance'
        if self.status != 'maintenance':
            if self.is_full:
                self.status = 'full'
            else:
                self.status = 'available'
        super().save(*args, **kwargs)

    def validate_assignment(self, user):
        """Validate if a user can be assigned to this room."""
        if self.is_full:
            raise ValueError(f"Room {self.room_number} is full.")
        if not isinstance(user, settings.AUTH_USER_MODEL):
            raise ValueError("Invalid user assignment. Must be a User instance.")

class Occupancy(models.Model):
    # This links your Custom User to a Room
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='room_assignment'
    )
    room = models.ForeignKey(
        Room, 
        on_delete=models.CASCADE, 
        related_name='room_occupants'
    )
    check_in_date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Occupancies"
    
    def __str__(self):
        return f"{self.student.full_name} in {self.room.room_number}"