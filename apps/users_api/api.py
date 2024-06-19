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
    retrieve,
    confirm,
    reset_request,
    reset,
)


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        abs_url_func = request.build_absolute_uri
        status_code, data = register(
            data=data,
            abs_url_func=abs_url_func,
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
        status_code, data = retrieve(
            user=user,
        )
        return Response(
            data=data,
            status=status_code,
        )


class ConfirmEmailView(APIView):
    def get(self, request, url_hash, *args, **kwargs):
        status_code, data = confirm(
            url_hash=url_hash,
        )
        return Response(
            data=data,
            status=status_code,
        )


class PasswordResetRequestView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        abs_url_func = request.build_absolute_uri
        status_code, data = reset_request(
            data=data,
            abs_url_func = abs_url_func,
        )
        return Response(
            data=data,
            status=status_code,
        )


class PasswordResetView(APIView):
    def post(self, request, url_hash, *args, **kwargs):
        data = request.data
        status_code, data = reset(
            url_hash=url_hash,
            data=data,
        )
        return Response(
            data=data,
            status=status_code,
        )