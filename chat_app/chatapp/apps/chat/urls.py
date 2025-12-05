# apps/chat/urls.py
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('room/<uuid:room_id>/', views.chat_room, name='chat_room'),
    path('create/', views.create_chat, name='create_chat'),
]