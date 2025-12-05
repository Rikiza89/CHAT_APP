from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserProfileForm
from .models import User, UserProfile


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
            UserProfile.objects.create(user=user)
            auth_login(request, user)
            return redirect('chat:chat_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    posts = user.posts.filter(is_public=True)[:10]
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