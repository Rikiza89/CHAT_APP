# apps/accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, FriendRequest, Friendship


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'is_online', 'last_seen', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'is_online']
    search_fields = ['username', 'email']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'avatar', 'status_message', 'is_online', 
                      'oauth_provider', 'oauth_id', 'blocked_users')
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'show_online_status', 'created_at']
    search_fields = ['user__username', 'user__email']
    list_filter = ['show_online_status', 'show_last_seen']


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['from_user__username', 'to_user__username']


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ['user1', 'user2', 'created_at']
    search_fields = ['user1__username', 'user2__username']