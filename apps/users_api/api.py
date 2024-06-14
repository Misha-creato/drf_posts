from rest_framework.parsers import (
    MultiPartParser,
    FormParser,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from users_api.services import (
    authenticate_user,
    create_user,
    update_user,
    get_user,
    delete_user,
)


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        status_code, data = create_user(
            data=data,
        )
        return Response(
            data=data,
            status=status_code,
        )


class AuthView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        status_code, data = authenticate_user(
            data=data,
        )
        return Response(
            data=data,
            status=status_code,
        )


class CustomUserView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, *args, **kwargs):
        user = request.user
        status_code, data = get_user(
            user=user,
        )
        return Response(
            data=data,
            status=status_code,
        )

    def patch(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        status_code, data = update_user(
            user=user,
            data=data,
        )
        return Response(
            data=data,
            status=status_code,
        )

    def delete(self, request, *args, **kwargs):
        user = request.user
        status_code, data = delete_user(
            user=user,
        )
        return Response(
            data=data,
            status=status_code,
        )


class ConfirmEmailView(APIView):
    def get(self, url_hash, *args, **kwargs):
        pass

# class PasswordResetView(APIView):
#     def post(self, url_hash, *args, **kwargs):
#         pass
