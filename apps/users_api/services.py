import uuid
from typing import Callable

from django.contrib.auth import authenticate
from django.http.request import QueryDict
from django.urls import reverse

from notifications.services import Email
from users_api.models import (
    CustomUser,
    CustomToken,
)
from users_api.serializers import (
    RegisterSerializer,
    CustomUserSerializer,
)

from utils.logger import (
    get_logger,
    get_log_user_data,
)
from utils.response_patterns import generate_response


logger = get_logger(__name__)


def register(data: QueryDict, abs_url_func: Callable) -> (int, dict):
    user_data = get_log_user_data(
        user_data=dict(data),
    )
    logger.info(
        msg=f'Создание пользователя {user_data}',
    )

    serializer = RegisterSerializer(
        data=data,
    )
    if not serializer.is_valid():
        logger.error(
            msg=f'Невалидные данные для создания пользователя {user_data}: {serializer.errors}',
        )
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
        logger.error(
            msg=f'Возникла ошибка при попытке создать пользователя {user_data}',
            exc_info=True,
        )
        return generate_response(
            status_code=500,
        )

    logger.info(
        msg=f'Пользователь {user_data} успешно создан',
    )

    status = send_email_by_type(
        user=user,
        abs_url_func=abs_url_func,
        email_type='confirm_email',
    )
    if status != 200:
        return generate_response(
            status_code=206,
        )

    return generate_response(
        status_code=200,
    )


def auth(data: QueryDict) -> (int, dict):
    email = data.get('email')
    password = data.get('password')
    logger.info(
        msg=f'Вход пользователя {email}',
    )

    user = authenticate(
        email=email,
        password=password,
    )
    if user is None:
        logger.error(
            msg=f'Невалидные данные пользователя {email}',
        )
        return generate_response(
            status_code=401,
        )

    try:
        token, _ = CustomToken.objects.get_or_create(user=user)
    except Exception as exc:
        logger.error(
            msg=f'Ошибка при попытке получить токен пользователя {email}',
            exc_info=True,
        )
        return generate_response(
            status_code=500,
        )

    key = token.key
    data = {
        'token': key,
    }
    logger.info(
        msg=f'Токен {key} пользователя {email} получен',
    )
    return generate_response(
        status_code=200,
        data=data,
    )


def detail(user: CustomUser) -> (int, dict):
    logger.info(
        msg=f'Получение данных пользователя {user}',
    )
    serializer = CustomUserSerializer(
        instance=user,
    )
    data = serializer.data
    logger.info(
        msg=f'Данные пользователя {user} успешно получены: {data}',
    )
    return generate_response(
        status_code=200,
        data=data,
    )


def update(user: CustomUser, data: QueryDict) -> (int, dict):
    user_data = get_log_user_data(
        user_data=dict(data),
    )
    logger.info(
        msg=f'Обновление данных пользователя {user}: {user_data}',
    )

    serializer = CustomUserSerializer(
        instance=user,
        data=data,
    )
    if not serializer.is_valid():
        logger.error(
            msg=f'Невалидные данные для обновления пользователя {user} {user_data}: {serializer.errors}',
        )
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
        logger.error(
            msg=f'Возникла ошибка при попытке обновить данные пользователя {user}: {user_data}',
            exc_info=True,
        )
        return generate_response(
            status_code=500,
        )

    data = serializer.data
    logger.info(
        msg=f'Обновление данных пользователя {user}: {user_data} прошло успешно',
    )
    return generate_response(
        status_code=200,
        data=data,
    )


def retrieve(user: CustomUser) -> (int, dict):
    email = user.email
    logger.info(
        msg=f'Удаление пользователя {email}',
    )
    try:
        user.delete()
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при удалении пользователя {email}',
            exc_info=True,
        )
        return generate_response(
            status_code=500,
        )

    logger.info(
        msg=f'Пользователь {email} успешно удален',
    )
    return generate_response(
        status_code=200,
    )


def send_email_by_type(user: CustomUser, abs_url_func: Callable, email_type: str) -> int:
    logger.info(
        msg=f'Получение данных для формирования текста письма {email_type} пользователю {user}',
    )

    url_hash = str(uuid.uuid4())
    user.url_hash = url_hash

    try:
        user.save()
    except Exception as exc:
        logger.error(
            msg=f'Не удалось получить данные для формирования текста письма {email_type} \
                        пользователю {user}',
            exc_info=True,
        )
        return 500

    url = abs_url_func(reverse(email_type, args=(user.url_hash,)))
    mail_data = {
        'url': url,
    }

    logger.info(
        msg=f'Данные для формирования текста письма {email_type} \
            пользователю {user} получены: {mail_data}',
    )

    email = Email(
        email_type=email_type,
        mail_data=mail_data,
        recipient=user,
    )
    status = email.send()
    return status


def get_user_by(**kwargs) -> (int, CustomUser | None):
    logger.info(
        msg=f'Поиск пользователя с {kwargs}',
    )
    try:
        user = CustomUser.objects.filter(
            **kwargs,
        ).first()
    except Exception as exc:
        logger.error(
            msg=f'Ошибка при поиске пользователя с {kwargs}',
            exc_info=True,
        )
        return 500, None

    if user is None:
        logger.error(
            msg=f'Пользователь с {kwargs} не найден',
        )
        return 400, None

    logger.info(
        msg=f'Пользователь {user} с {kwargs} найден',
    )
    return 200, user


def confirm(url_hash: str) -> (int, dict):
    logger.info(
        msg=f'Подтверждение email пользователя с хэшем {url_hash}',
    )

    status_code, user = get_user_by(
        url_hash=url_hash,
    )
    if status_code != 200:
        return generate_response(
            status_code=status_code,
        )

    user.email_confirmed = True
    user.url_hash = None
    try:
        user.save()
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при попытке подтвердить email пользователя {user}',
            exc_info=True,
        )
        return generate_response(
            status_code=500,
        )

    logger.info(
        msg=f'Пользователь {user} с успешно подтвердил email',
    )
    return generate_response(
        status_code=200,
    )


def reset(url_hash: str, data: QueryDict) -> (int, dict):
    logger.info(
        msg=f'Сброс пароля пользователя с хэшем {url_hash}',
    )

    status_code, user = get_user_by(
        url_hash=url_hash,
    )
    if status_code != 200:
        return generate_response(
            status_code=status_code,
        )

    user_data = get_log_user_data(
        user_data=dict(data),
    )
    logger.info(
        msg=f'Сброс пароля пользователя {user}: {user_data}',
    )
    serializer = CustomUserSerializer(
        instance=user,
        data=data,
    )
    if not serializer.is_valid():
        logger.error(
            msg=f'Невалидные данные для сброса пароля пользователя {user} {user_data}: {serializer.errors}',
        )
        return generate_response(
            status_code=400,
        )

    validated_data = serializer.validated_data
    user.set_password(validated_data['password'])
    user.url_hash = None
    try:
        user.save()
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при сбросe пароля пользователя {user} {user_data}: {serializer.errors}',
            exc_info=True,
        )
        return generate_response(
            status_code=500,
        )

    logger.info(
        msg=f'Пароль пользователя {user} {user_data} успешно сброшен',
    )
    return generate_response(
        status_code=200,
    )


def reset_request(data: QueryDict, abs_url_func: Callable) -> (int, dict):
    email = data.get('email')
    logger.info(
        msg=f'Запрос на сброс пароля пользователя {email}',
    )

    serializer = CustomUserSerializer(
        data=data,
    )
    if not serializer.is_valid():
        logger.error(
            msg=f'Невалидные данные для запроса на сброс пароля пользователя {email}: {serializer.errors}',
        )
        return generate_response(
            status_code=400,
        )

    status_code, user = get_user_by(
        email=email,
    )
    if status_code != 200:
        return generate_response(
            status_code=status_code,
        )

    status_code = send_email_by_type(
        user=user,
        email_type='password_reset',
        abs_url_func=abs_url_func,
    )

    logger.info(
        msg=f'Запрос на сброс пароля пользователя {email} прошел успешно',
    )
    return generate_response(
        status_code=status_code,
    )
