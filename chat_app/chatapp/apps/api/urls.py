# apps/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .v1.accounts import AuthViewSet, UserViewSet
from .v1.chat import ChatRoomViewSet, MessageViewSet
from .v1.blog import PostViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'chat/rooms', ChatRoomViewSet, basename='chatroom')
router.register(r'chat/messages', MessageViewSet, basename='message')
router.register(r'blog/posts', PostViewSet, basename='post')
router.register(r'blog/comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('auth/register/', AuthViewSet.as_view({'post': 'register'}), name='register'),
    path('auth/login/', AuthViewSet.as_view({'post': 'login'}), name='login'),
    path('', include(router.urls)),
]