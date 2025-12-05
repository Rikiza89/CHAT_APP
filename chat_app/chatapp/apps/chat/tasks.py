from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Message, ChatRoom, ChatMembership
from apps.accounts.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@shared_task
def send_message_notification(message_id):
    """Send push notification for new message"""
    try:
        message = Message.objects.select_related('sender', 'room').get(id=message_id)
        room = message.room
        
        # Get all members except sender
        members = room.members.exclude(id=message.sender.id)
        
        for member in members:
            membership = ChatMembership.objects.get(user=member, room=room)
            
            # Skip if user muted the chat
            if membership.muted:
                continue
            
            # Send email notification if user is offline
            if not member.is_online:
                send_mail(
                    subject=f'New message from {message.sender.username}',
                    message=f'{message.sender.username}: {message.content[:100]}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[member.email],
                    fail_silently=True,
                )
        
        return f"Notifications sent for message {message_id}"
    except Message.DoesNotExist:
        return f"Message {message_id} not found"


@shared_task
def process_file_upload(message_id):
    """Process uploaded file (compress images, generate thumbnails, etc.)"""
    try:
        from PIL import Image
        import os
        
        message = Message.objects.get(id=message_id)
        
        if message.message_type == 'image' and message.file:
            # Generate thumbnail
            img = Image.open(message.file.path)
            img.thumbnail((200, 200))
            
            # Save thumbnail
            thumb_path = message.file.path.replace(
                os.path.basename(message.file.path),
                f'thumb_{os.path.basename(message.file.path)}'
            )
            img.save(thumb_path)
            
            # Update message with thumbnail path
            message.thumbnail = thumb_path
            message.save()
        
        return f"File processed for message {message_id}"
    except Exception as e:
        return f"Error processing file: {str(e)}"


@shared_task
def update_message_status(message_id, status):
    """Update message delivery/read status"""
    try:
        message = Message.objects.get(id=message_id)
        message.status = status
        message.save(update_fields=['status'])
        
        # Broadcast status update via WebSocket
        channel_layer = get_channel_layer()
        room_group_name = f'chat_{message.room.id}'
        
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'message_status_update',
                'message_id': str(message_id),
                'status': status
            }
        )
        
        return f"Message {message_id} status updated to {status}"
    except Message.DoesNotExist:
        return f"Message {message_id} not found"


@shared_task
def clean_old_messages():
    """Clean up deleted messages older than 30 days"""
    from django.utils import timezone
    from datetime import timedelta
    
    threshold_date = timezone.now() - timedelta(days=30)
    
    deleted_count = Message.objects.filter(
        is_deleted=True,
        deleted_at__lt=threshold_date
    ).delete()[0]
    
    return f"Cleaned up {deleted_count} old deleted messages"


@shared_task
def send_daily_summary():
    """Send daily summary of unread messages to users"""
    from collections import defaultdict
    
    users = User.objects.filter(is_active=True, is_online=False)
    
    for user in users:
        unread_count = defaultdict(int)
        
        memberships = ChatMembership.objects.filter(user=user)
        
        for membership in memberships:
            count = Message.objects.filter(
                room=membership.room,
                created_at__gt=membership.last_read_at
            ).exclude(sender=user).count()
            
            if count > 0:
                unread_count[membership.room.name or "Direct Message"] = count
        
        if unread_count:
            message_text = "You have unread messages:\n\n"
            for room_name, count in unread_count.items():
                message_text += f"- {room_name}: {count} unread\n"
            
            send_mail(
                subject='Daily Message Summary',
                message=message_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
    
    return f"Daily summary sent to {users.count()} users"


@shared_task
def update_user_online_status():
    """Update user online status based on last activity"""
    from django.utils import timezone
    from datetime import timedelta
    
    threshold = timezone.now() - timedelta(minutes=5)
    
    # Set users as offline if they haven't been active in 5 minutes
    updated = User.objects.filter(
        is_online=True,
        last_seen__lt=threshold
    ).update(is_online=False)
    
    return f"Updated online status for {updated} users"