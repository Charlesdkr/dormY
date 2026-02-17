from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Occupancy

@receiver([post_save, post_delete], sender=Occupancy)
def update_room_status_on_occupancy_change(sender, instance, **kwargs):
    """
    This signal handler is triggered whenever an Occupancy record is saved or deleted.
    
    It automatically calls the save() method on the related room, which contains
    the logic to update the room's status to 'full' or 'available' based on
    its current occupancy.
    """
    # The instance is an Occupancy object, so we can get its room and save it.
    # This will trigger the save() method in the Room model.
    instance.room.save()