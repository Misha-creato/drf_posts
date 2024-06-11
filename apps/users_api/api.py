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
    get_user, delete_user,
)


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        status_code, data = create_user(
            request=request,
        )
        return Response(
            data,
            status=status_code,
        )


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        status_code, data = authenticate_user(
            request=request,
        )
        return Response(
            data,
            status=status_code,
        )


class CustomUserView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, *args, **kwargs):
        status_code, data = get_user(
            request=request,
        )
        return Response(
            data,
            status=status_code,
        )

    def patch(self, request, *args, **kwargs):
        status_code, data = update_user(
            request=request,
        )
        return Response(
            data,
            status=status_code,
        )

    def delete(self, request, *args, **kwargs):
        status_code, data = delete_user(
            request=request,
        )
        return Response(
            data,
            status=status_code,
        )
