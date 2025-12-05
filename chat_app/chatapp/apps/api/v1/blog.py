# apps/api/v1/blog.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from apps.blog.models import Post, Comment, PostLike, CommentLike
from apps.blog.serializers import PostSerializer, CommentSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(is_public=True).select_related('author')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        author_id = self.request.query_params.get('author_id')
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        post = self.get_object()
        post.view_count += 1
        post.save(update_fields=['view_count'])
        serializer = self.get_serializer(post)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, slug=None):
        post = self.get_object()
        PostLike.objects.get_or_create(post=post, user=request.user)
        return Response({'status': 'liked'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unlike(self, request, slug=None):
        post = self.get_object()
        PostLike.objects.filter(post=post, user=request.user).delete()
        return Response({'status': 'unliked'})
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def feed(self, request):
        posts = Post.objects.filter(is_public=True).order_by('-created_at')[:20]
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        post_slug = self.request.query_params.get('post_slug')
        if post_slug:
            return Comment.objects.filter(
                post__slug=post_slug,
                parent=None
            ).select_related('author').order_by('-created_at')
        return Comment.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        comment = self.get_object()
        CommentLike.objects.get_or_create(comment=comment, user=request.user)
        return Response({'status': 'liked'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unlike(self, request, pk=None):
        comment = self.get_object()
        CommentLike.objects.filter(comment=comment, user=request.user).delete()
        return Response({'status': 'unliked'})