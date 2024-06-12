from typing import Any

from django.contrib.auth import authenticate

from users_api.models import (
    CustomUser,
    CustomToken,
)
from users_api.serializers import (
    RegisterSerializer,
    CustomUserSerializer,
)

from utils.custom_handler import logger
from utils.log_data import get_log_user_data
from utils.response_patterns import generate_response


def create_user(request: Any) -> (int, dict):
    data = request.data
    serializer = RegisterSerializer(
        data=data,
    )
    user_data = get_log_user_data(
        user_data=data.dict(),
    )
    logger.info(f'Создание пользователя {user_data}')
    if not serializer.is_valid():
        logger.error(f'Невалидные данные для создания '
                     f'пользователя {user_data}: {serializer.errors}')
        return generate_response(
            status_code=400,
        )

    validated_data = serializer.validated_data
    try:
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
        )
    except Exception as exc:
        logger.error(f'Возникла ошибка при попытке создать '
                     f'пользователя {user_data}', exc_info=True)
        return generate_response(
            status_code=500,
        )

    logger.info(f'Пользователь {user_data} успешно создан')
    return generate_response(
        status_code=200,
    )


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
        return generate_response(
            status_code=401,
        )

    try:
        token, _ = CustomToken.objects.get_or_create(user=user)
    except Exception as exc:
        logger.error(f'Ошибка при попытке получить токен пользователя {email}', exc_info=True)
        return generate_response(
            status_code=500,
        )

    if token is None:
        logger.error(f'Токен пользователя {email} не найден')
        return generate_response(
            status_code=404,
        )

    key = token.key
    data = {
        'token': key,
    }
    logger.info(f'Токен {key} пользователя {email} получен')
    return generate_response(
        status_code=200,
        data=data,
    )


def get_user(request: Any) -> (int, dict):
    user = request.user
    logger.info(f'Получение данных пользователя {user}')
    serializer = CustomUserSerializer(user)
    data = serializer.data
    logger.info(f'Данные пользователя {user} успешно получены: {data}')
    return generate_response(
        status_code=200,
        data=data,
    )


def update_user(request: Any) -> (int, dict):
    user = request.user
    data = request.data
    user_data = get_log_user_data(
        user_data=data.dict(),
    )
    logger.info(f'Обновление данных пользователя {user}: {user_data}')
    serializer = CustomUserSerializer(
        user,
        data=data,
    )
    if not serializer.is_valid():
        logger.error(f'Невалидные данные для обновления '
                     f'пользователя {user} {user_data}: {serializer.errors}')
        return generate_response(
            status_code=400,
        )

    validated_data = serializer.validated_data
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
        return generate_response(
            status_code=500,
        )

    data = serializer.data
    logger.info(f'Обновление данных пользователя {user}: {user_data} прошло успешно')
    return generate_response(
        status_code=200,
        data=data,
    )


def delete_user(request: Any) -> (int, dict):
    user = request.user
    email = user.email
    logger.info(f'Удаление пользователя {email}')
    try:
        user.delete()
    except Exception as exc:
        logger.error(f'Возникла ошибка при удалении '
                     f'пользователя {email}', exc_info=True)
        return generate_response(
            status_code=500,
        )

    logger.info(f'Пользователь {email} успешно удален')
    return generate_response(
        status_code=200,
    )
