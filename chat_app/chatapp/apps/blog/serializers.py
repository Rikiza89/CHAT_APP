# apps/blog/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Comment, PostLike, CommentLike, PostMedia
from apps.accounts.serializers import UserSerializer

User = get_user_model()


class PostMediaSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = PostMedia
        fields = ['id', 'media_type', 'file', 'file_url', 'thumbnail', 'order']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.file.url) if request else obj.file.url
        return None


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'parent',
                  'like_count', 'is_liked', 'replies', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at']
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False
    
    def get_replies(self, obj):
        if obj.parent is None:
            replies = obj.replies.all()[:5]
            return CommentSerializer(replies, many=True, context=self.context).data
        return []


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    media = PostMediaSerializer(many=True, read_only=True)
    recent_comments = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'author', 'title', 'content', 'slug', 'image',
                  'video_url', 'media', 'like_count', 'comment_count',
                  'is_liked', 'recent_comments', 'view_count', 'is_public',
                  'created_at', 'updated_at', 'published_at']
        read_only_fields = ['id', 'author', 'slug', 'view_count', 'created_at']
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False
    
    def get_recent_comments(self, obj):
        comments = obj.comments.filter(parent=None)[:3]
        return CommentSerializer(comments, many=True, context=self.context).data