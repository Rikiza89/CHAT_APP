# apps/api/v1/chat.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Max
from apps.chat.models import ChatRoom, Message, ChatMembership
from apps.chat.serializers import ChatRoomSerializer, MessageSerializer, ChatMemberSerializer


class ChatRoomViewSet(viewsets.ModelViewSet):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ChatRoom.objects.filter(members=self.request.user).annotate(
            last_message_time=Max('messages__created_at')
        ).order_by('-last_message_time')
    
    def create(self, request):
        room_type = request.data.get('room_type', 'direct')
        member_ids = request.data.get('member_ids', [])
        
        if room_type == 'direct' and len(member_ids) == 1:
            # Check if direct room already exists
            other_user_id = member_ids[0]
            existing_room = ChatRoom.objects.filter(
                room_type='direct',
                members=request.user
            ).filter(members__id=other_user_id).first()
            
            if existing_room:
                serializer = self.get_serializer(existing_room)
                return Response(serializer.data)
        
        # Create new room
        room = ChatRoom.objects.create(
            room_type=room_type,
            name=request.data.get('name'),
            created_by=request.user
        )
        
        # Add members
        ChatMembership.objects.create(user=request.user, room=room, role='admin')
        for user_id in member_ids:
            ChatMembership.objects.create(user_id=user_id, room=room)
        
        serializer = self.get_serializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        room = self.get_object()
        user_id = request.data.get('user_id')
        
        if room.room_type != 'group':
            return Response({'error': 'Can only add members to groups'}, status=400)
        
        membership = ChatMembership.objects.filter(user=request.user, room=room).first()
        if not membership or membership.role != 'admin':
            return Response({'error': 'Only admins can add members'}, status=403)
        
        ChatMembership.objects.get_or_create(user_id=user_id, room=room)
        return Response({'status': 'member added'})
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        room = self.get_object()
        ChatMembership.objects.filter(user=request.user, room=room).delete()
        return Response({'status': 'left room'})
    
    @action(detail=True, methods=['delete'])
    def delete_chat(self, request, pk=None):
        room = self.get_object()
        ChatMembership.objects.filter(user=request.user, room=room).delete()
        
        # If no members left, delete room
        if not room.members.exists():
            room.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        room_id = self.request.query_params.get('room_id')
        if room_id:
            return Message.objects.filter(
                room_id=room_id,
                room__members=self.request.user,
                is_deleted=False
            ).select_related('sender', 'reply_to').order_by('-created_at')
        return Message.objects.none()
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        room_id = request.data.get('room')
        if not ChatMembership.objects.filter(user=request.user, room_id=room_id).exists():
            return Response({'error': 'Not a member of this room'}, status=403)
        
        message = serializer.save(sender=request.user)
        return Response(self.get_serializer(message).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'])
    def soft_delete(self, request, pk=None):
        message = self.get_object()
        if message.sender != request.user:
            return Response({'error': 'Can only delete own messages'}, status=403)
        
        from django.utils import timezone
        message.is_deleted = True
        message.deleted_at = timezone.now()
        message.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        room_id = request.query_params.get('room_id')
        query = request.query_params.get('q', '')
        
        messages = Message.objects.filter(
            room_id=room_id,
            room__members=request.user,
            content__icontains=query,
            is_deleted=False
        )[:50]
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)