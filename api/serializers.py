from rest_framework import serializers
from rest_framework.reverse import reverse

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import User, Profile, Tag, Post, Comment, Like, BookmarkItem, Follow, List

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'id', 'password', 'email']
        extra_kwargs = {'password' : {'write_only' : True}}
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data.get('email')
        user = User(**validated_data)

        try:
            validate_password(password, user)
        except ValidationError as e:
            raise serializers.ValidationError({'password' : e.messages}) 
        
        email_exists = User.objects.filter(email=email).exists()
        if email_exists:
            raise serializers.ValidationError({'email' : 'This email is already registered!'})

        user.set_password(password)
        user.save()
        return {
            'message' : 'User succesfully created!',
            'username' : user.username,
            'email' : user.email
        }

class AuthorSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='user.id')
    username = serializers.ReadOnlyField(source='user.username')
    about = serializers.ReadOnlyField(source='user.profile.about')
    follower_details = serializers.SerializerMethodField()

    def get_follower_details(self, obj):

        request = self.context.get('request')
        
        follower_count = Follow.objects.filter(followed=obj).count()
        following_count = Follow.objects.filter(follower=obj).count()

        if request.user.is_authenticated:
            profile = Profile.objects.get(id = request.user.id)
            is_following = True if Follow.objects.filter(follower=profile, followed=obj).exists() else False
        else:
            is_following = False

        return {
            'is_following' : is_following,
            'follower_count' : follower_count,
            'follower_list': reverse('follower_list', kwargs={'profile_id' : obj.id}, request=request),
            'following_count' : following_count,
            'following_list': reverse('following_list', kwargs={'profile_id' : obj.id}, request=request)
        }

    class Meta:
        model = Profile
        fields = ['id', 'username', 'about', 'follower_details']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class PostDetailSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    tag = TagSerializer(many=True)
    like_details = serializers.SerializerMethodField()
    comment_details = serializers.SerializerMethodField()
    bookmark_details = serializers.SerializerMethodField()

    class Meta:
        model = Post
        exclude = ['likes']

    def get_like_details(self, obj):

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user_liked = obj.likes.filter(id=request.user.id).exists()
        else:
            user_liked = False

        return {
            'user_liked': user_liked,
            'count': obj.likes.count(),
            'liked_users': reverse('post_likes', kwargs={'post_id': obj.id}, request=request),
        }

    def get_comment_details(self, obj):
        
        request = self.context.get('request')
        comments = Comment.objects.filter(post=obj)
        return {
            'count': comments.count(),
            'comments': reverse('post_comments', kwargs={'post_id': obj.id}, request=request),
        }
    
    def get_bookmark_details(self, obj):
        request = self.context.get('request')
        bookmark_details = {
            'bookmarked_any' : False,
            'lists' : {}
        }
        if request and request.user.is_authenticated:
            lists = List.objects.filter(user=request.user)

            for list in lists:
                bookmark_details['lists'][list.id] = {
                    'name': list.name,
                    'post_in_list' : BookmarkItem.objects.filter(post=obj, user=request.user, list=list).exists()
                }

            bookmark_details['bookmarked_any'] = any([item['post_in_list'] for item in bookmark_details['lists'].values()])

        return bookmark_details

class PostCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = '__all__'

class LikeDetailSerializer(serializers.ModelSerializer):
    user = AuthorSerializer(source='user.profile')

    class Meta:
        model = Like
        fields = ['user','created_at']

class LikeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.body = validated_data.get('body', instance.body)
        instance.save()
        return instance

class RecursiveCommentSerializer(serializers.ModelSerializer):
    sub_comments = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'body', 'author', 'created_at', 'updated_at', 'sub_comments']

    def get_sub_comments(self, obj):
        sub_comments = Comment.objects.filter(parent_comment=obj)
        if sub_comments.exists():
            serializer = RecursiveCommentSerializer(sub_comments, many=True)
            return serializer.data
        return []

class CommentListSerializer(serializers.ModelSerializer):
    sub_comments = RecursiveCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'body', 'author', 'post', 'parent_comment', 'created_at', 'updated_at', 'sub_comments']

class FollowerListSerializer(serializers.ModelSerializer):
    follower = AuthorSerializer()

    class Meta:
        model = Follow
        fields = ['follower']

class FollowingListSerializer(serializers.ModelSerializer):
    followed = AuthorSerializer()

    class Meta:
        model = Follow
        fields = ['followed']

class FollowCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = []

class ListSerializer(serializers.ModelSerializer):

    class Meta:
        model = List
        fields = '__all__'

class BookmarkItemSerializer(serializers.ModelSerializer):
    post = PostDetailSerializer()

    class Meta:
        model = BookmarkItem
        fields = ['post', 'created_at']

class BookmarkCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = BookmarkItem
        fields = []

class ListDetailSerializer(serializers.ModelSerializer):
    
    posts = BookmarkItemSerializer(many=True, read_only=True)


    # def get_posts(self, obj):
    #     posts = BookmarkItem.objects.filter(list=obj)
    #     return {
    #         'count': posts.count(),
    #         'posts': serializers.Serializer(BookmarkItem),
    #     }

    class Meta:
        model = List
        fields = '__all__'