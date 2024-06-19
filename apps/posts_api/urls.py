from django.urls import path

from posts_api.api import (
    PostListView,
    PostDetailView,
    # PostView,
)


urlpatterns = [
    path(
        '<str:slug>/',
        PostDetailView.as_view(),
        name='post',
    ),
    path(
        '',
        PostListView.as_view(),
        name='posts',
    ),
    # path(
    #     '',
    #     PostView.as_view(),
    #     name='posts',
    # ),
]
