from django.http import Http404

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import IsOwnerOrReadOnly

from .models import User, Profile, Tag, Post, Comment, Like, Bookmark, Follow
from .serializers import PostDetailSerializer, PostCreateSerializer, LikeCreateSerializer, LikeDetailSerializer, UserSerializer, CommentCreateSerializer, CommentListSerializer, FollowCreateSerializer, FollowingListSerializer, FollowerListSerializer
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


class LikeListCreateView(SetAuthorMixin, generics.ListCreateAPIView):

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

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        try:
            post = Post.objects.get(id=post_id)
            return Like.objects.filter(post=post)
        except Post.DoesNotExist:
            raise Http404(f'No post found with ID {post_id}!')


class CommentListCreateView(SetAuthorMixin, generics.ListCreateAPIView):

    def get_serializer_class(self):

        if self.request.method == 'GET':
            return CommentListSerializer
        elif self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return CommentCreateSerializer
        
    def get_queryset(self):
        post_id = self.kwargs['post_id']
        try:
            post = Post.objects.get(id=post_id)
            return Comment.objects.filter(post=post, parent_comment=None)
        except Post.DoesNotExist:
            raise Http404(f'No post found with ID {post_id}!')


class CommentDetailView(SetAuthorMixin, generics.RetrieveUpdateDestroyAPIView):

    queryset = Comment.objects.all()
    serializer_class = CommentListSerializer


class FollowCreateView(SetAuthorMixin, generics.CreateAPIView):
    
    queryset = Follow.objects.all()
    serializer_class = FollowCreateSerializer
    
    def create(self, request, *args, **kwargs):
        
        profile_id = kwargs.get('profile_id')
        
        try:
            follower_profile = Profile.objects.get(user=request.user)
            target_profile = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            return Response({'detail': 'No such profile. Make sure to provide correct profile id!'}, status=status.HTTP_404_NOT_FOUND)

        if follower_profile == target_profile:
            return Response({'detail': 'Users cannot follow themselves!'}, status=status.HTTP_403_FORBIDDEN)

        existing_follow, created = Follow.objects.get_or_create(follower=follower_profile, followed=target_profile)

        if created:
            return Response({'detail': 'User followed successfully.'}, status=status.HTTP_201_CREATED)
        else:
            existing_follow.delete()
            return Response({'detail': 'Follow removed successfully.'}, status=status.HTTP_204_NO_CONTENT)


class FollowersListView(generics.ListAPIView):
    
    serializer_class = FollowerListSerializer
    
    def get_queryset(self):
        profile_id = self.kwargs.get('profile_id')
        profile = Profile.objects.get(id=profile_id)
        queryset = Follow.objects.filter(followed=profile)
        return queryset


class FollowingListView(generics.ListAPIView):
    
    serializer_class = FollowingListSerializer
    
    def get_queryset(self):
        profile_id = self.kwargs.get('profile_id')
        profile = Profile.objects.get(id=profile_id)
        queryset = Follow.objects.filter(follower=profile)
        return queryset
