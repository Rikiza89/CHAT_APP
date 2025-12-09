from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Post, Comment, PostLike
from apps.accounts.models import Notification
from django.utils.text import slugify
import uuid


@receiver(pre_save, sender=Post)
def generate_slug(sender, instance, **kwargs):
    """Generate slug for post if not exists"""
    if not instance.slug:
        if instance.title:
            base_slug = slugify(instance.title[:50])
        else:
            base_slug = str(uuid.uuid4())[:8]
        instance.slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"


@receiver(post_save, sender=Comment)
def notify_comment(sender, instance, created, **kwargs):
    """Notify post author about new comment"""
    if created and instance.author != instance.post.author:
        # Check if user wants comment notifications
        if hasattr(instance.post.author, 'profile') and instance.post.author.profile.notify_comments:
            Notification.objects.create(
                recipient=instance.post.author,
                sender=instance.author,
                notification_type='comment',
                message=f'{instance.author.username} commented on your post',
                link=f'/post/{instance.post.slug}/'
            )


@receiver(post_save, sender=PostLike)
def notify_like(sender, instance, created, **kwargs):
    """Notify post author about new like"""
    if created and instance.user != instance.post.author:
        # Check if user wants like notifications
        if hasattr(instance.post.author, 'profile') and instance.post.author.profile.notify_likes:
            Notification.objects.create(
                recipient=instance.post.author,
                sender=instance.user,
                notification_type='like',
                message=f'{instance.user.username} liked your post',
                link=f'/post/{instance.post.slug}/'
            )