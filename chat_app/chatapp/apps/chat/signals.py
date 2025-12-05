# apps/chat/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message
from .tasks import send_message_notification, update_message_status


@receiver(post_save, sender=Message)
def handle_new_message(sender, instance, created, **kwargs):
    """Handle new message - send notifications"""
    if created:
        pass
        # Send notification asynchronously
        # send_message_notification.delay(str(instance.id))
        
        # # Update status to delivered
        # update_message_status.delay(str(instance.id), 'delivered')