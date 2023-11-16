import os
import random
import shutil
from typing import Iterable, Optional
from PIL import Image, ImageDraw, ImageFont
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify

# Create your models here.

class User(AbstractUser):
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Profile.objects.get_or_create(user=self)
        List.objects.get_or_create(user=self, public=False, name='Reading List')

    def __str__(self):
        return self.username

def get_upload_path(instance, filename):
    return os.path.join('profile_pictures', instance.user.username, filename)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.TextField(max_length=5000, default='', blank=True)
    profile_picture = models.ImageField(upload_to=get_upload_path, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} profile'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        #implement a way to delete old profile pictures!
        if not self.profile_picture:
            random_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

            image = Image.new('RGB', (300, 300), color=random_color)

            first_letter = self.user.username[0].upper()

            draw = ImageDraw.Draw(image)
            font = ImageFont.load_default(size=288)
            text_position = (75,-50)
            draw.text(text_position, first_letter, font=font, fill=(255, 255, 255))

            user_directory = os.path.join('media/profile_pictures', self.user.username)
            os.makedirs(user_directory, exist_ok=True)
            filename = f'{self.user.username}_profile_picture.png'
            file_path = os.path.join('profile_pictures', self.user.username, filename)
            image.save(f'media/{file_path}')

            # Update the profile_picture field
            self.profile_picture = file_path
            self.save()
    
    def delete(self, *args, **kwargs):

        if self.profile_picture:
            shutil.rmtree(os.path.join('media/profile_pictures', self.user.username))

        super().delete(*args, **kwargs)


class Tag(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Tag, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

def upload_cover_image(instance, filename):
    username = instance.author.user.username
    post_id = instance.id
    path = f'media/cover_images/{username}/post_{post_id}/'
    return os.path.join(path, filename)

class Post(models.Model):
    title = models.CharField(max_length=250)
    body = models.TextField(max_length=5000)
    tag = models.ManyToManyField(Tag)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, through='Like', related_name='liked_posts')
    read_length_minutes = models.IntegerField(null=True, default=0)
    cover_image = models.ImageField(upload_to=upload_cover_image, null=True, default=None)

    def __str__(self):
        return f'{self.author.user.username} profile'
    
    def save(self, *args, **kwargs):
        self.read_length_minutes = round(len(self.body.split(' ')) * 0.25 / 60)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']


class Comment(models.Model):
    body = models.TextField(max_length=5000)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, related_name='sub_comments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class List(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    public = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)


class BookmarkItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name='posts')

    class Meta:
        ordering = ['-created_at']


class Follow(models.Model):
    follower = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='following')
    followed = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.follower.user.username} followed {self.followed.user.username}'


class Notification(models.Model):
    pass
