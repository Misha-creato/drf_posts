from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from users_api.serializers import (
    RegisterSerializer,
    CustomUserSerializer,
)
from users_api.services import authenticate_user


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(
            data=request.data,
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        status_code, response = authenticate_user(
            request=request,
        )
        return Response(
            data=response,
            status=status_code,
        )


class CustomUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response(
            data=serializer.data,
        )

    # def patch(self, request, pk, *args, **kwargs):
    #     user = request.user
    #     serializer = CustomUserSerializer(
    #         user,
    #         data=request.data,
    #     )
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(
    #             data=serializer.data,
    #         )
    #     return Response(
    #         data=serializer.errors,
    #         status=status.HTTP_400_BAD_REQUEST,
    #     )

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = CustomUserSerializer(
            user,
            data=request.data,
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                data=serializer.data,
            )
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
