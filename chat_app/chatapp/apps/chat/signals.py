from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message
from apps.accounts.models import Notification


@receiver(post_save, sender=Message)
def handle_new_message(sender, instance, created, **kwargs):
    """Create notification for new message"""
    if created:
        room_members = instance.room.members.exclude(id=instance.sender.id)
        for member in room_members:
            # Check if user wants message notifications
            if hasattr(member, 'profile') and member.profile.notify_messages:
                Notification.objects.create(
                    recipient=member,
                    sender=instance.sender,
                    notification_type='message',
                    message=f'{instance.sender.username} sent you a message',
                    link=f'/chat/room/{instance.room.id}/'
                )