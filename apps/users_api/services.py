import logging
from typing import Any

from django.contrib.auth import authenticate

from rest_framework import status

from users_api.models import (
    CustomUser,
    CustomToken,
)
from users_api.serializers import (
    RegisterSerializer,
    CustomUserSerializer,
)


logger = logging.getLogger(__name__)


def get_log_user_data(user_data: dict) -> dict:
    data = user_data.copy()
    keys = [
        'password',
        'confirm_password',
        'new_password',
    ]
    for key in keys:
        data.pop(key, None)
    return data


def create_user(request: Any) -> (int, dict):
    serializer = RegisterSerializer(
        data=request.data,
    )
    if not serializer.is_valid():
        return status.HTTP_400_BAD_REQUEST, {
            'message': 'Error',
            'data': serializer.errors,
        }
    validated_data = serializer.validated_data
    email = validated_data['email']
    user_data = get_log_user_data(
        user_data=validated_data,
    )
    logger.info(f'Создание пользователя {user_data}')
    try:
        user = CustomUser.objects.create_user(
            email=email,
            password=validated_data['password'],
        )
    except Exception as exc:
        logger.error(f'Возникла ошибка при попытке создать '
                     f'пользователя {user_data}', exc_info=True)
        return status.HTTP_500_INTERNAL_SERVER_ERROR, {
            'message': 'Fail',
            'data': user_data,
        }
    logger.info(f'Пользователь {user_data} успешно создан')
    return status.HTTP_201_CREATED, {
        'message': 'Success',
        'data': user_data,
    }


def authenticate_user(request: Any) -> (int, dict):
    email = request.data.get('email')
    password = request.data.get('password')
    logger.info(f'Вход пользователя {email}')
    user = authenticate(
        email=email,
        password=password,
    )
    if user is None:
        logger.error(f'Невалидные данные пользователя {email}')
        return status.HTTP_401_UNAUTHORIZED, {
            'message': 'Fail',
            'data': 'Неправильный адрес электронной почты или пароль',
        }

    try:
        token, created = CustomToken.objects.get_or_create(user=user)
    except Exception as exc:
        logger.error(f'Ошибка при попытке получить токен пользователя {email}', exc_info=True)
        return status.HTTP_500_INTERNAL_SERVER_ERROR, {
            'message': 'Error',
            'data': 'Возникла ошибка',
        }

    if token is None:
        logger.error(f'Токен пользователя {email} не найден')
        return status.HTTP_404_NOT_FOUND, {
            'message': 'Fail',
            'data': 'Возникла ошибка',
        }

    key = token.key
    data = {
        'token': key,
        'email': email,
    }
    logger.info(f'Токен {key} пользователя {email} получен')
    return status.HTTP_200_OK, {
        'message': 'Success',
        'data': data,
    }


def get_user(request: Any) -> (int, dict):
    user = request.user
    serializer = CustomUserSerializer(user)
    return status.HTTP_200_OK, {
        'message': 'Success',
        'data': serializer.data
    }


def update_user(request: Any) -> (int, dict):
    user = request.user
    serializer = CustomUserSerializer(
        user,
        data=request.data,
    )
    if not serializer.is_valid():
        return status.HTTP_400_BAD_REQUEST, {
            'message': 'Error',
            'data': serializer.errors,
        }
    validated_data = serializer.validated_data
    user_data = get_log_user_data(
        user_data=validated_data,
    )
    logger.info(f'Обновление данных пользователя {user}: {user_data}')
    for key, value in validated_data.items():
        if key == 'password':
            user.set_password(value)
        else:
            setattr(user, key, value)
    try:
        user.save()
    except Exception as exc:
        logger.error(f'Возникла ошибка при попытке обновить '
                     f'данные пользователя {user}: {user_data}', exc_info=True)
        return status.HTTP_500_INTERNAL_SERVER_ERROR, {
            'message': 'Error',
            'data': 'Возникла ошибка',
        }

    logger.info(f'Обновление данных пользователя {user}: {user_data} прошло успешно')
    return status.HTTP_200_OK, {
        'message': 'Success',
        'data': user_data,
    }


def delete_user(request: Any) -> (int, dict):
    user = request.user
    logger.info(f'Удаление пользователя {user}')
    try:
        user.delete()
    except Exception as exc:
        logger.error(f'Возникла ошибка при удалении '
                     f'пользователя {user}', exc_info=True)
        return status.HTTP_500_INTERNAL_SERVER_ERROR, {
            'message': 'Error',
            'data': 'Возникла ошибка',
        }

    logger.info(f'Пользователь успешно удален')
    return status.HTTP_204_NO_CONTENT, {
        'message': 'Success',
        'data': 'Пользователь успешно удален',
    }