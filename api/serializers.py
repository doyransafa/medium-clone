from rest_framework import serializers
from rest_framework.reverse import reverse

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import User, Profile, Tag, Post, Comment, Like, Bookmark, Follow

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'id', 'password', 'email']
        extra_kwargs = {'password' : {'write_only' : True}}
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data.get('email')
        print(email)
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

    class Meta:
        model = Profile
        fields = ['id', 'username', 'about']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class PostDetailSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    tag = TagSerializer(many=True)
    like_details = serializers.SerializerMethodField()
    comment_details = serializers.SerializerMethodField()

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
            'comment_details': reverse('post_comments', kwargs={'post_id': obj.id}, request=request),
        }


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
