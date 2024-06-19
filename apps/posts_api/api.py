from rest_framework.permissions import (
    BasePermission,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from posts_api.services import (
    get_posts,
    add,
    detail,
    update,
    delete,
)


class CreateOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return bool(request.user and request.user.is_authenticated)
        return True


class PostListView(APIView):
    permission_classes = [CreateOrReadOnly]

    def get(self, request, *args, **kwargs):
        status_code, data = get_posts()
        return Response(
            status=status_code,
            data=data,
        )

    def post(self, request, *args, **kwargs):
        print(self.get_permissions())
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


# class PostUserView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request, pk, *args, **kwargs):
#         status_code, data = get_posts()
#         return Response(
#             status=status_code,
#             data=data,
#         )
#

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
        status_code, data = delete(
            slug=slug,
            user=user,
        )
        return Response(
            status=status_code,
            data=data,
        )
