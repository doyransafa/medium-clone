import os
import random
import shutil
from PIL import Image, ImageDraw, ImageFont
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
import uuid
from django.core.files.storage import default_storage


# Create your models here.

class User(AbstractUser):
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Profile.objects.get_or_create(user=self)
        List.objects.get_or_create(user=self, public=False, name='Reading List')

    def __str__(self):
        return self.username


def get_default_image_path(username):
    # Generate a default image (similar to what you've done)
    random_color = (random.randint(0, 255), random.randint(
        0, 255), random.randint(0, 255))
    image = Image.new('RGB', (300, 300), color=random_color)
    first_letter = username[0].upper()
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=288)
    text_position = (75, -50)
    draw.text(text_position, first_letter, font=font, fill=(255, 255, 255))

    # Save the image to the default storage (S3 bucket)
    filename = f'{username}_profile_picture.png'
    file_path = os.path.join('profile_pictures', username, filename)
    image_io = default_storage.open(file_path, 'wb')
    image.save(image_io, format='PNG')
    image_io.close()
    
    return file_path


def get_upload_path(instance, filename):
    return os.path.join('profile_pictures', instance.user.username, filename)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.TextField(max_length=5000, default='', blank=True)
    profile_picture = models.ImageField(upload_to=get_upload_path, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} profile'
    
    def save(self, *args, **kwargs):

        if not self.profile_picture:
            # Generate default image path
            default_image_path = get_default_image_path(self.user.username)
            self.profile_picture = default_image_path

        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):

        if self.profile_picture:
            shutil.rmtree(os.path.join('profile_pictures', self.user.username))

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
    id = uuid.uuid4()
    path = f'cover_images/{username}/{id}/{filename}'
    return path

class Post(models.Model):
    title = models.CharField(max_length=250)
    body = models.TextField(max_length=5000)
    tag = models.ManyToManyField(Tag)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, through='Like', related_name='liked_posts')
    read_length_minutes = models.IntegerField(null=True, default=0)
    cover_image = models.ImageField(upload_to=upload_cover_image, null=True, default='')

    def __str__(self):
        return f'{self.author.user.username} profile'
    
    def save(self, *args, **kwargs):
        self.read_length_minutes = round(len(self.body.split(' ')) * 0.25 / 60)
        super().save(*args, **kwargs)  # If it's not a new post, proceed with normal save




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
