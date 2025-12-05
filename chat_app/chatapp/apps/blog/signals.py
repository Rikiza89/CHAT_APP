# apps/blog/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Post
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
