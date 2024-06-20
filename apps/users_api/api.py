from rest_framework.parsers import (
    MultiPartParser,
    FormParser,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from users_api.services import (
    auth,
    register,
    update,
    detail,
    confirm_email,
    password_restore_request,
    password_restore,
    remove,
)


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        get_url_func = request.build_absolute_uri
        status_code, data = register(
            data=data,
            get_url_func=get_url_func,
        )
        return Response(
            data=data,
            status=status_code,
        )


class AuthView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        status_code, data = auth(
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
        status_code, data = detail(
            user=user,
        )
        return Response(
            data=data,
            status=status_code,
        )

    def patch(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        status_code, data = update(
            user=user,
            data=data,
        )
        return Response(
            data=data,
            status=status_code,
        )

    def delete(self, request, *args, **kwargs):
        user = request.user
        status_code, data = remove(
            user=user,
        )
        return Response(
            data=data,
            status=status_code,
        )


class ConfirmEmailView(APIView):
    def get(self, request, url_hash, *args, **kwargs):
        status_code, data = confirm_email(
            url_hash=url_hash,
        )
        return Response(
            data=data,
            status=status_code,
        )


class PasswordRestoreRequestView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        get_url_func = request.build_absolute_uri
        status_code, data = password_restore_request(
            data=data,
            get_url_func=get_url_func,
        )
        return Response(
            data=data,
            status=status_code,
        )


class PasswordRestoreView(APIView):
    def post(self, request, url_hash, *args, **kwargs):
        data = request.data
        status_code, data = password_restore(
            url_hash=url_hash,
            data=data,
        )
        return Response(
            data=data,
            status=status_code,
        )
