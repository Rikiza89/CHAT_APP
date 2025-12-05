# apps/chat/middleware.py
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from urllib.parse import parse_qs

User = get_user_model()


@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """Custom middleware for JWT authentication in WebSocket"""
    
    async def __call__(self, scope, receive, send):
        # Parse query string for token
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]
        
        if token:
            try:
                # Validate token
                UntypedToken(token)
                # Decode token to get user_id
                from rest_framework_simplejwt.tokens import AccessToken
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                scope['user'] = await get_user(user_id)
            except (InvalidToken, TokenError):
                scope['user'] = AnonymousUser()
        else:
            # Try to get user from session (for template-based auth)
            if 'session' in scope:
                from channels.auth import get_user as channels_get_user
                scope['user'] = await channels_get_user(scope)
            else:
                scope['user'] = AnonymousUser()
        
        return await super().__call__(scope, receive, send)
