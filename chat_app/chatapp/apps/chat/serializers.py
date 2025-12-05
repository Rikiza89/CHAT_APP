# apps/chat/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message, ChatMembership, MessageReaction
from apps.accounts.serializers import UserSerializer

User = get_user_model()


class ChatMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ChatMembership
        fields = ['id', 'user', 'role', 'muted', 'last_read_at', 'joined_at']


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    reply_to = serializers.SerializerMethodField()
    reactions = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'message_type', 'content', 
                  'file', 'file_url', 'file_name', 'file_size', 'reply_to',
                  'reactions', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'sender', 'status', 'created_at']
    
    def get_reply_to(self, obj):
        if obj.reply_to:
            return {
                'id': str(obj.reply_to.id),
                'sender': obj.reply_to.sender.username,
                'content': obj.reply_to.content[:100]
            }
        return None
    
    def get_reactions(self, obj):
        reactions = {}
        for reaction in obj.reactions.all():
            emoji = reaction.emoji
            if emoji not in reactions:
                reactions[emoji] = []
            reactions[emoji].append({
                'user_id': str(reaction.user.id),
                'username': reaction.user.username
            })
        return reactions
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.file.url) if request else obj.file.url
        return None


class ChatRoomSerializer(serializers.ModelSerializer):
    members = ChatMemberSerializer(source='chatmembership_set', many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'room_type', 'name', 'description', 'avatar',
                  'members', 'last_message', 'unread_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_last_message(self, obj):
        last_msg = obj.get_last_message()
        if last_msg:
            return MessageSerializer(last_msg, context=self.context).data
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            membership = obj.chatmembership_set.filter(user=request.user).first()
            if membership:
                return obj.messages.filter(
                    created_at__gt=membership.last_read_at
                ).exclude(sender=request.user).count()
        return 0