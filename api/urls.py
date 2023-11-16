from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import PostListCreateView, PostDetailView, LikeListCreateView, RegisterUserView, CommentListCreateView, CommentDetailView, FollowCreateView, FollowersListView, FollowingListView, ListListCreateView, ListDetailsView, BookmarkItemCreateView, UpdateProfileView, ProfileDetailsView, UserPostListView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('register', RegisterUserView.as_view(), name='token_refresh'),

    path('posts', PostListCreateView.as_view(), name='post_list_create'),
    path('posts/<int:profile_id>', UserPostListView.as_view(), name='user_posts'),
    path('post/<int:pk>', PostDetailView.as_view(), name='post_details'),

    path('like/<int:post_id>', LikeListCreateView.as_view(), name='post_likes'),
    path('comment/<int:post_id>', CommentListCreateView.as_view(), name='post_comments'),
    path('comment/<int:comment_id>', CommentDetailView.as_view(), name='comment_details'),
    path('bookmark/add/<int:post_id>/<int:list_id>', BookmarkItemCreateView.as_view(), name='bookmark_toggle'), ##
    # path('bookmark/<int:post_id>', CommentListCreateView.as_view(), name='bookmark_details'), ##
    
    path('profile/<int:profile_id>/follow', FollowCreateView.as_view(), name='follow_unfollow'),
    path('profile/<int:profile_id>/followers', FollowersListView.as_view(), name='follower_list'),
    path('profile/<int:profile_id>/following', FollowingListView.as_view(), name='following_list'),
    path('profile/<int:pk>/update', UpdateProfileView.as_view(), name='update_profile_details'),
    path('profile/<int:pk>', ProfileDetailsView.as_view(), name='profile_details'),
    
    path('lists/<int:profile_id>', ListListCreateView.as_view(), name='lists'), ## add private - public differentiation for own lists!
    path('list/<int:profile_id>/<pk>', ListDetailsView.as_view(), name='list_details'), ##
    
    # Schema/Docs endpoints:
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)