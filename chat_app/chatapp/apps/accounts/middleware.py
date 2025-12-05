# apps/accounts/middleware.py
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class UpdateLastSeenMiddleware:
    """Update user's last_seen timestamp on each request"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            User.objects.filter(pk=request.user.pk).update(
                last_seen=timezone.now()
            )
        
        response = self.get_response(request)
        return response