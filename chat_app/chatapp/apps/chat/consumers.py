from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
import json
from datetime import datetime
from .models import ChatRoom, Message, MessageReadReceipt, ChatMembership
from apps.accounts.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Check if user is member of room
        is_member = await self.check_membership()
        if not is_member:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Update user online status
        await self.update_online_status(True)
        
        # Notify others user is online
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user_id': str(self.user.id),
                'username': self.user.username,
                'is_online': True
            }
        )
    
    async def disconnect(self, close_code):
        # Update user online status
        await self.update_online_status(False)
        
        # Notify others user is offline
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user_id': str(self.user.id),
                'username': self.user.username,
                'is_online': False
            }
        )
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'send_message':
            await self.handle_send_message(data)
        elif action == 'typing':
            await self.handle_typing(data)
        elif action == 'read':
            await self.handle_read_receipt(data)
        elif action == 'react':
            await self.handle_reaction(data)
    
    async def handle_send_message(self, data):
        message_type = data.get('message_type', 'text')
        content = data.get('content', '')
        reply_to_id = data.get('reply_to')
        
        # Save message to database
        message = await self.save_message(
            message_type=message_type,
            content=content,
            reply_to_id=reply_to_id
        )
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': await self.serialize_message(message)
            }
        )
    
    async def handle_typing(self, data):
        is_typing = data.get('is_typing', False)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': str(self.user.id),
                'username': self.user.username,
                'is_typing': is_typing
            }
        )
    
    async def handle_read_receipt(self, data):
        message_id = data.get('message_id')
        
        if message_id:
            await self.mark_as_read(message_id)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'read_receipt',
                    'message_id': message_id,
                    'user_id': str(self.user.id),
                    'username': self.user.username
                }
            )
    
    async def handle_reaction(self, data):
        message_id = data.get('message_id')
        emoji = data.get('emoji')
        
        if message_id and emoji:
            await self.add_reaction(message_id, emoji)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_reaction',
                    'message_id': message_id,
                    'user_id': str(self.user.id),
                    'username': self.user.username,
                    'emoji': emoji
                }
            )
    
    # WebSocket event handlers
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'data': event['message']
        }))
    
    async def typing_indicator(self, event):
        # Don't send typing indicator to the user who's typing
        if event['user_id'] != str(self.user.id):
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing']
            }))
    
    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'status',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_online': event['is_online']
        }))
    
    async def read_receipt(self, event):
        await self.send(text_data=json.dumps({
            'type': 'read',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
            'username': event['username']
        }))
    
    async def message_reaction(self, event):
        await self.send(text_data=json.dumps({
            'type': 'reaction',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
            'username': event['username'],
            'emoji': event['emoji']
        }))
    
    # Database operations
    @database_sync_to_async
    def check_membership(self):
        try:
            return ChatMembership.objects.filter(
                user=self.user,
                room_id=self.room_id
            ).exists()
        except:
            return False
    
    @database_sync_to_async
    def save_message(self, message_type, content, reply_to_id=None):
        reply_to = None
        if reply_to_id:
            try:
                reply_to = Message.objects.get(id=reply_to_id)
            except Message.DoesNotExist:
                pass
        
        message = Message.objects.create(
            room_id=self.room_id,
            sender=self.user,
            message_type=message_type,
            content=content,
            reply_to=reply_to
        )
        return message
    
    @database_sync_to_async
    def serialize_message(self, message):
        return {
            'id': str(message.id),
            'sender': {
                'id': str(message.sender.id),
                'username': message.sender.username,
                'avatar': message.sender.avatar.url if message.sender.avatar else None
            },
            'message_type': message.message_type,
            'content': message.content,
            'reply_to': str(message.reply_to.id) if message.reply_to else None,
            'status': message.status,
            'created_at': message.created_at.isoformat()
        }
    
    @database_sync_to_async
    def update_online_status(self, is_online):
        User.objects.filter(id=self.user.id).update(is_online=is_online)
    
    @database_sync_to_async
    def mark_as_read(self, message_id):
        try:
            message = Message.objects.get(id=message_id)
            MessageReadReceipt.objects.get_or_create(
                message=message,
                user=self.user
            )
            
            # Update message status if all members have read
            room_members_count = message.room.members.count()
            read_count = message.read_receipts.count()
            
            if read_count >= room_members_count - 1:  # Exclude sender
                message.status = 'read'
                message.save(update_fields=['status'])
        except Message.DoesNotExist:
            pass
    
    @database_sync_to_async
    def add_reaction(self, message_id, emoji):
        from .models import MessageReaction
        try:
            message = Message.objects.get(id=message_id)
            MessageReaction.objects.get_or_create(
                message=message,
                user=self.user,
                emoji=emoji
            )
        except Message.DoesNotExist:
            pass