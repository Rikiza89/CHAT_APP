# apps/chat/admin.py
from django.contrib import admin
from .models import ChatRoom, ChatMembership, Message, MessageReadReceipt, MessageReaction


class ChatMembershipInline(admin.TabularInline):
    model = ChatMembership
    extra = 0


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'room_type', 'name', 'created_by', 'created_at']
    list_filter = ['room_type', 'created_at']
    search_fields = ['name', 'members__username']
    inlines = [ChatMembershipInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'room', 'sender', 'message_type', 'status', 'is_deleted', 'created_at']
    list_filter = ['message_type', 'status', 'is_deleted', 'created_at']
    search_fields = ['content', 'sender__username', 'room__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(MessageReadReceipt)
class MessageReadReceiptAdmin(admin.ModelAdmin):
    list_display = ['message', 'user', 'read_at']
    search_fields = ['user__username', 'message__content']


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = ['message', 'user', 'emoji', 'created_at']
    list_filter = ['emoji', 'created_at']
    search_fields = ['user__username', 'message__content']
