# apps/blog/urls.py
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.feed, name='feed'),
    path('post/create/', views.create_post, name='create_post'),  # Move BEFORE slug pattern
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('user/<uuid:user_id>/posts/', views.user_posts, name='user_posts'),
]