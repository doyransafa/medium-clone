from django.http import Http404
from django.db.models import Q

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser

from .permissions import IsOwnerOrReadOnly
from .models import User, Profile, Post, Comment, Like, Follow, List, BookmarkItem
from .serializers import (PostDetailSerializer, PostCreateSerializer, LikeCreateSerializer, LikeDetailSerializer, UserSerializer, CommentCreateSerializer, 
                            CommentListSerializer, FollowCreateSerializer, FollowingListSerializer, FollowerListSerializer, ListSerializer, ListDetailSerializer, 
                            BookmarkCreateSerializer, ProfileInformationSerializer, ProfileDetailSerializer)
from .mixins import SetAuthorMixin

from drf_spectacular.utils import extend_schema

class RegisterUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

class UpdateProfileView(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileInformationSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsOwnerOrReadOnly]

class PostListCreateView(SetAuthorMixin, generics.ListCreateAPIView):

    queryset = Post.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):

        queryset = Post.objects.all()

        tag = self.request.query_params.get('tag')
        search = self.request.query_params.get('search', '')
        following = self.request.query_params.get('following', False)

        if tag:
            queryset = queryset.filter(tag__slug=tag)
        if search:
            queryset = queryset.filter(title__icontains=search)
        if following and following.lower() == 'true':
            user_profile = Profile.objects.get(user=self.request.user)
            following_profiles = Follow.objects.filter(follower=user_profile).values_list('followed', flat=True)
            queryset = queryset.filter(Q(author__in=following_profiles))

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
    parser_classes = [MultiPartParser, FormParser]

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

@extend_schema(summary='Add or list all likes of specified post', description='GET = List of all likes. POST = Add a like to the post. Post request can be empty object!')
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

@extend_schema(summary='Add or list all comments of specified post', description='GET = List of all comments. POST = Add a comment to the post.')
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


@extend_schema(summary='CRUD operations for individual comments', description='CRUD operations for individual comments')
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

class ListListCreateView(SetAuthorMixin, generics.ListCreateAPIView):

    serializer_class = ListSerializer
    queryset = List.objects.all()

    def get_queryset(self):
        profile_id = self.kwargs.get('profile_id')
        user = User.objects.get(id=profile_id)
        queryset = List.objects.filter(user=user)
        return queryset
    
class ListDetailsView(SetAuthorMixin, generics.RetrieveUpdateDestroyAPIView):
    
    def get_queryset(self):
        profile_id = self.kwargs.get('profile_id')
        list_id = self.kwargs.get('list_id')
        user = User.objects.get(id=profile_id)
        queryset = List.objects.filter(user=user)
        return queryset
    
    def get_serializer_class(self):

        if self.request.method == 'GET':
            return ListDetailSerializer
        elif self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return ListSerializer

class BookmarkItemCreateView(SetAuthorMixin, generics.CreateAPIView):

    serializer_class = BookmarkCreateSerializer
    
    def create(self, request, *args, **kwargs):
        
        post_id = kwargs.get('post_id')
        list_id = kwargs.get('list_id')
        
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'detail': 'No such post. Make sure to provide correct post id!'}, status=status.HTTP_404_NOT_FOUND)
        try:
            list = List.objects.get(id=list_id, user=request.user)
        except List.DoesNotExist:
            return Response({'detail': 'No such list or somebody elses list. Make sure to provide correct list id!'}, status=status.HTTP_404_NOT_FOUND)

        bookmark_item, created = BookmarkItem.objects.get_or_create(post=post, list=list, user=request.user)

        if created:
            return Response({'detail': 'Item added to the list successfully.'}, status=status.HTTP_201_CREATED)
        else:
            bookmark_item.delete()
            return Response({'detail': 'Item removed from the list successfully.'}, status=status.HTTP_204_NO_CONTENT)
        

class ProfileDetailsView(generics.RetrieveAPIView):
    serializer_class = ProfileDetailSerializer
    queryset = Profile.objects.all()


class UserPostListView(generics.ListAPIView):

    serializer_class = PostDetailSerializer
    
    def get_queryset(self):

        profile_id = self.kwargs.get('profile_id')
        return Post.objects.filter(author__user__id=profile_id)

        # return super().get_queryset()