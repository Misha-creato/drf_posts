from django.urls import path

from posts_api.api import (
    PostListView,
    PostDetailView,
    PostUserView,
)


urlpatterns = [
    path(
        '<str:slug>/',
        PostDetailView.as_view(),
        name='post',
    ),
    path(
        'author/<int:pk>/',
        PostUserView.as_view(),
        name='author_posts',
    ),
    path(
        '',
        PostListView.as_view(),
        name='posts',
    ),
]
