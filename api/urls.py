from django.urls import path
from .views import PostListCreateView, PostDetailView, LikeListCreateView, RegisterUserView, CommentListCreateView, CommentDetailView, FollowCreateView, FollowersListView, FollowingListView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView



urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('register', RegisterUserView.as_view(), name='token_refresh'),

    path('posts', PostListCreateView.as_view(), name='post_list_create'),
    path('post/<int:pk>', PostDetailView.as_view(), name='post_details'),

    path('post/<int:post_id>/like', LikeListCreateView.as_view(), name='post_likes'),
    path('post/<int:post_id>/comment', CommentListCreateView.as_view(), name='post_comments'),
    path('comment/<int:comment_id>', CommentDetailView.as_view(), name='comment_details'),
    
    path('profile/<int:profile_id>/follow', FollowCreateView.as_view(), name='follow_unfollow'),
    path('profile/<int:profile_id>/followers', FollowersListView.as_view(), name='follower_list'),
    path('profile/<int:profile_id>/following', FollowingListView.as_view(), name='following_list'),
    
]