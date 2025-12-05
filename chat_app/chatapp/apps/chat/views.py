# apps/chat/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max
from .models import ChatRoom, Message, ChatMembership
from apps.accounts.models import User


@login_required
def chat_list(request):
    rooms = ChatRoom.objects.filter(members=request.user).annotate(
        last_message_time=Max('messages__created_at')
    ).order_by('-last_message_time')
    
    return render(request, 'chat/chat_list.html', {'rooms': rooms})


@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id, members=request.user)
    messages = room.messages.filter(is_deleted=False).select_related('sender')[:50]
    members = room.members.all()
    
    return render(request, 'chat/chat_room.html', {
        'room': room,
        'messages': reversed(messages),
        'members': members
    })


@login_required
def create_chat(request):
    if request.method == 'POST':
        user_ids = request.POST.getlist('users')
        room_type = request.POST.get('room_type', 'direct')
        
        if room_type == 'direct' and len(user_ids) == 1:
            # Check existing direct chat
            other_user = get_object_or_404(User, id=user_ids[0])
            existing = ChatRoom.objects.filter(
                room_type='direct',
                members=request.user
            ).filter(members=other_user).first()
            
            if existing:
                return redirect('chat:chat_room', room_id=existing.id)
        
        # Create new room
        room = ChatRoom.objects.create(
            room_type=room_type,
            name=request.POST.get('name'),
            created_by=request.user
        )
        
        ChatMembership.objects.create(user=request.user, room=room, role='admin')
        for user_id in user_ids:
            ChatMembership.objects.create(user_id=user_id, room=room)
        
        return redirect('chat:chat_room', room_id=room.id)
    
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chat/create_chat.html', {'users': users})
