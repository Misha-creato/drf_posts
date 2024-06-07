import logging

from django.contrib.auth import authenticate

from rest_framework.exceptions import APIException
from rest_framework import status

from users_api.models import (
    CustomUser,
    CustomToken,
)


logger = logging.getLogger(__name__)


def create_user(validated_data: dict) -> CustomUser:
    email = validated_data['email']
    logger.info(f'Создание пользователя {email}')
    try:
        user = CustomUser.objects.create_user(
            email=email,
            password=validated_data['password'],
        )
    except Exception as exc:
        logger.error(f'Возникла ошибка при попытке создать пользователя {email}', exc_info=True)
        raise APIException
    logger.info(f'Пользователь {email} успешно создан')
    return user


def authenticate_user(request) -> dict:
    email = request.data.get('email')
    password = request.data.get('password')
    logger.info(f'Вход пользователя {email}')
    user = authenticate(
        email=email,
        password=password,
    )
    if user is None:
        logger.warning(f'Невалидные данные пользователя {email}')
        return {
            'code': status.HTTP_401_UNAUTHORIZED,
            'message': {
                'error': 'Невалидные данные',
            }
        }
    try:
        token, created = CustomToken.objects.get_or_create(user=user)
    except Exception as exc:
        logger.error(f'Ошибка при попытке получить токен пользователя {email}', exc_info=True)
        return {
            'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': {
                'error': 'Ошибка при поиске токена пользователя',
            }
        }
    if token is None:
        logger.warning(f'Токен пользователя {email} не найден')
        return {
            'code': status.HTTP_404_NOT_FOUND,
            'message': {
                'error': 'Токен для пользователя не найден',
            }
        }
    key = token.key
    logger.info(f'Токен {key} пользователя {email} получен')
    return {
            'code': status.HTTP_200_OK,
            'message': {
                'token': key,
                'email': email,
            }
        }


def update_user(user: CustomUser, validated_data: dict) -> dict: # TODO
    print(validated_data)
    email = user.email
    logger.info(f'Обновление данных пользователя {email}')
    for key, value in validated_data.items():
        setattr(user, key, value)
    try:
        user.save()
    except Exception as exc:
        logger.error(f'Возникла ошибка при попытке обновить данные пользователя {email}', exc_info=True)
        raise APIException
    logger.info(f'Обновление данных пользователя {email} прошло успешно')
    return {
        'code': status.HTTP_200_OK,
        'message': validated_data,
    }
