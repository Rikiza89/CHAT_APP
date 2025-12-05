from django.db import models
from django.conf import settings
from django.utils.text import slugify
import uuid


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    
    # Media
    image = models.ImageField(upload_to='blog_posts/%Y/%m/', blank=True, null=True)
    video_url = models.URLField(blank=True)
    
    # Engagement
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, through='PostLike', related_name='liked_posts')
    view_count = models.PositiveIntegerField(default=0)
    
    # Privacy
    is_public = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'posts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['slug']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title[:50]) if self.title else str(uuid.uuid4())[:8]
            self.slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title or f"Post by {self.author.username}"
    
    def like_count(self):
        return self.likes.count()
    
    def comment_count(self):
        return self.comments.count()


class PostLike(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'post_likes'
        unique_together = ['post', 'user']
        indexes = [
            models.Index(fields=['post', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} likes {self.post.id}"


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    
    content = models.TextField(max_length=1000)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Engagement
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, through='CommentLike', related_name='liked_comments')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'comments'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['parent']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.id}"
    
    def like_count(self):
        return self.likes.count()


class CommentLike(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'comment_likes'
        unique_together = ['comment', 'user']
    
    def __str__(self):
        return f"{self.user.username} likes comment {self.comment.id}"


class PostMedia(models.Model):
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('gif', 'GIF'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    file = models.FileField(upload_to='blog_media/%Y/%m/')
    thumbnail = models.ImageField(upload_to='blog_thumbnails/%Y/%m/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'post_media'
        ordering = ['order']
        indexes = [
            models.Index(fields=['post', 'order']),
        ]
    
    def __str__(self):
        return f"{self.media_type} for post {self.post.id}"