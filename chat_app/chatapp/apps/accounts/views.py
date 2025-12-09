from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserProfileForm
from .models import User, UserProfile, Notification

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('username')  # Form field is 'username'
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            auth_login(request, user)
            return redirect('chat:chat_list')
        else:
            return render(request, 'accounts/login.html', {
                'error': 'Invalid email or password'
            })
    
    return render(request, 'accounts/login.html')


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # UserProfile.objects.create(user=user)
            auth_login(request, user)
            return redirect('chat:chat_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    posts = user.posts.filter(is_public=True)[:10]
    
    # Create view notification - check settings
    if request.user != user:
        if hasattr(user, 'profile') and user.profile.notify_views:
            Notification.objects.create(
                recipient=user,
                sender=request.user,
                notification_type='view',
                message=f'{request.user.username} viewed your profile',
                link=f'/accounts/profile/{request.user.id}/'
            )
    
    return render(request, 'accounts/profile.html', {
        'profile_user': user,
        'posts': posts
    })

@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile', user_id=request.user.id)
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
def notifications(request):
    notifications = request.user.notifications.all()[:20]
    # Mark as read
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'accounts/notifications.html', {'notifications': notifications})

@login_required
def notification_count(request):
    from django.http import JsonResponse
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'count': count})

@login_required
def notification_settings(request):
    profile = request.user.profile
    
    if request.method == 'POST':
        profile.notify_messages = request.POST.get('notify_messages') == 'on'
        profile.notify_comments = request.POST.get('notify_comments') == 'on'
        profile.notify_likes = request.POST.get('notify_likes') == 'on'
        profile.notify_views = request.POST.get('notify_views') == 'on'
        profile.save()
        return redirect('accounts:notification_settings')
    
    return render(request, 'accounts/notification_settings.html', {'profile': profile})