from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from posts_api.services import (
    get_posts,
    add,
    detail,
    update,
    remove,
    get_posts_by_pk,
)


class PostListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        status_code, data = get_posts()
        return Response(
            status=status_code,
            data=data,
        )

    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        status_code, data = add(
            user=user,
            data=data,
        )
        return Response(
            status=status_code,
            data=data,
        )


class PostUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        user = request.user
        status_code, data = get_posts_by_pk(
            pk=pk,
            user=user,
        )
        return Response(
            status=status_code,
            data=data,
        )


class PostDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug, *args, **kwargs):
        user = request.user
        status_code, data = detail(
            slug=slug,
            user=user,
        )
        return Response(
            status=status_code,
            data=data,
        )

    def patch(self, request, slug, *args, **kwargs):
        user = request.user
        data = request.data
        status_code, data = update(
            slug=slug,
            user=user,
            data=data,
        )
        return Response(
            status=status_code,
            data=data,
        )

    def delete(self, request, slug, *args, **kwargs):
        user = request.user
        status_code, data = remove(
            slug=slug,
            user=user,
        )
        return Response(
            status=status_code,
            data=data,
        )
