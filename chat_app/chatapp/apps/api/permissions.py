# apps/api/permissions.py
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj.author == request.user or obj.sender == request.user


class IsChatMember(permissions.BasePermission):
    """
    Custom permission to check if user is a member of the chat room.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if user is a member of the room
        if hasattr(obj, 'room'):
            return obj.room.members.filter(id=request.user.id).exists()
        elif hasattr(obj, 'members'):
            return obj.members.filter(id=request.user.id).exists()
        return False


class IsPostAuthor(permissions.BasePermission):
    """
    Custom permission to only allow post authors to edit/delete their posts.
    """
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
