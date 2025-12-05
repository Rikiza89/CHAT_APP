from django.db import models
from django.conf import settings
import uuid


class ChatRoom(models.Model):
    ROOM_TYPES = [
        ('direct', 'Direct Message'),
        ('group', 'Group Chat'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES, default='direct')
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='chat_rooms/%Y/%m/', blank=True, null=True)
    
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='ChatMembership', related_name='chat_rooms')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_rooms')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_rooms'
        indexes = [
            models.Index(fields=['room_type', 'created_at']),
        ]
    
    def __str__(self):
        if self.room_type == 'direct':
            members = self.members.all()[:2]
            return f"DM: {' & '.join([m.username for m in members])}"
        return self.name or f"Group {self.id}"
    
    def get_last_message(self):
        return self.messages.order_by('-created_at').first()


class ChatMembership(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    
    # Notification settings
    muted = models.BooleanField(default=False)
    muted_until = models.DateTimeField(null=True, blank=True)
    
    # Read tracking
    last_read_at = models.DateTimeField(auto_now_add=True)
    
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_memberships'
        unique_together = ['user', 'room']
        indexes = [
            models.Index(fields=['user', 'room']),
        ]
    
    def __str__(self):
        return f"{self.user.username} in {self.room}"


class Message(models.Model):
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('voice', 'Voice Note'),
        ('video', 'Video'),
    ]
    
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    content = models.TextField(blank=True)
    
    # Media fields
    file = models.FileField(upload_to='chat_files/%Y/%m/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='chat_thumbnails/%Y/%m/', blank=True, null=True)
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    
    # Reply functionality
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    
    # Status tracking
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')
    
    # Soft delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['room', '-created_at']),
            models.Index(fields=['sender', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"


class MessageReadReceipt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_receipts')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'message_read_receipts'
        unique_together = ['message', 'user']
        indexes = [
            models.Index(fields=['message', 'user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} read {self.message.id}"


class MessageReaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    emoji = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'message_reactions'
        unique_together = ['message', 'user', 'emoji']
        indexes = [
            models.Index(fields=['message', 'emoji']),
        ]
    
    def __str__(self):
        return f"{self.user.username} reacted {self.emoji} to {self.message.id}"