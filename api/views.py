from rest_framework import generics, status, response
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import IsOwnerOrReadOnly

from .models import User, Profile, Tag, Post, Comment, Like, Bookmark, Follow
from .serializers import PostDetailSerializer, PostCreateSerializer, LikeCreateSerializer, LikeDetailSerializer, UserSerializer
from .mixins import SetAuthorMixin

class RegisterUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

class PostListCreateView(SetAuthorMixin, generics.ListCreateAPIView):

    queryset = Post.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):

        queryset = Post.objects.all()

        tag = self.request.query_params.get('tag')
        search = self.request.query_params.get('search', '')

        if tag:
            queryset = queryset.filter(tag__id=tag)
        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset
    
    def get_serializer_class(self):

        if self.request.method == 'GET':
            return PostDetailSerializer
        elif self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return PostCreateSerializer

class PostDetailView(SetAuthorMixin, generics.RetrieveUpdateDestroyAPIView):

    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_serializer_class(self):

        if self.request.method == 'GET':
            return PostDetailSerializer
        elif self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return PostCreateSerializer
    
    def perform_update(self, serializer):
        # Ensure the author remains the same
        post_instance = self.get_object()
        serializer.validated_data['author'] = post_instance.author
        serializer.save()

class LikeView(SetAuthorMixin, generics.ListCreateAPIView):

    queryset = Like.objects.all()
    
    def create(self, request, *args, **kwargs):
        post_id = kwargs.get('post_id')
        post = Post.objects.get(id=post_id)

        existing_like = Like.objects.filter(post=post, user=request.user)

        if existing_like:
            existing_like.delete()
            return Response({'detail': 'Like removed successfully.'}, status=status.HTTP_204_NO_CONTENT)
        else:
            Like.objects.create(user=request.user, post=post)
            return Response({'detail': 'Post liked successfully.'}, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):

        if self.request.method == 'GET':
            return LikeDetailSerializer
        elif self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return LikeCreateSerializer