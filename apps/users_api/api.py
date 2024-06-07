import logging

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from users_api.serializers import (
    RegisterSerializer,
    CustomUserSerializer,
)
from users_api.services import authenticate_user, create_user, update_user


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(
            data=request.data,
        )
        if serializer.is_valid():
            create_user(
                validated_data=serializer.validated_data,
            )
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
        response = authenticate_user(
            request=request,
        )
        return Response(
            data=response['message'],
            status=response['code'],
        )


class CustomUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response(
            data=serializer.data,
        )

    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = CustomUserSerializer(
            user,
            data=request.data,
        )
        if serializer.is_valid():
            response = update_user(
                user=user,
                validated_data=serializer.validated_data,
            )
            return Response(
                data=response['message'],
                status=response['code'],
            )
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, *args, **kwargs): #TODO
        user = request.user
        user.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
