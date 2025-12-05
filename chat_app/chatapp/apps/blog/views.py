# apps/blog/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Post, Comment
from .forms import PostForm, CommentForm
from apps.accounts.models import User


def feed(request):
    posts = Post.objects.filter(is_public=True).select_related('author').order_by('-created_at')
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    return render(request, 'blog/feed.html', {'posts': posts})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post.view_count += 1
    post.save(update_fields=['view_count'])
    
    comments = post.comments.filter(parent=None).select_related('author')
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', slug=slug)
    else:
        form = CommentForm()
    
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form
    })


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = PostForm()
    return render(request, 'blog/create_post.html', {'form': form})


def user_posts(request, user_id):
    user = get_object_or_404(User, id=user_id)
    posts = Post.objects.filter(author=user, is_public=True).order_by('-created_at')
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    return render(request, 'blog/user_posts.html', {'profile_user': user, 'posts': posts})