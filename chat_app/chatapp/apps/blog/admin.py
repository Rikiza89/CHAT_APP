# apps/blog/admin.py
from django.contrib import admin
from .models import Post, Comment, PostLike, CommentLike, PostMedia


class PostMediaInline(admin.TabularInline):
    model = PostMedia
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'is_public', 'view_count', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['view_count', 'created_at', 'updated_at']
    inlines = [PostMediaInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'author', 'parent', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'author__username', 'post__title']
    raw_id_fields = ['post', 'author', 'parent']


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'created_at']
    search_fields = ['user__username', 'post__title']


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ['comment', 'user', 'created_at']
    search_fields = ['user__username']