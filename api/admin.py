from django.contrib import admin
from .models import User, Profile, Tag, Post, Comment, Like, BookmarkItem, Follow

# Register your models here.
admin.site.register((User, Profile, Tag, Post, Comment, Like, BookmarkItem, Follow))