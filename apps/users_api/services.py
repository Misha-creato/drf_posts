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
    PasswordRestoreSerializer,
)
from utils.constants import (
    CONFIRM_EMAIL,
    PASSWORD_RESTORE,
)

from utils.logger import (
    get_logger,
    get_log_user_data,
)
from utils.response_patterns import generate_response


logger = get_logger(__name__)


def register(data: QueryDict, get_url_func: Callable) -> (int, dict):
    '''
    Создание пользователя(регистрация)

    Args:
        data: данные пользователя
        get_url_func: функция для создания ссылки

    Returns:
        Кортеж из статуса и словаря данных
    '''

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
            msg=f'Невалидные данные для создания '
                f'пользователя {user_data}: {serializer.errors}',
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
        get_url_func=get_url_func,
        email_type=CONFIRM_EMAIL,
    )
    if status != 200:
        return generate_response(
            status_code=206,
        )

    return generate_response(
        status_code=200,
    )


def auth(data: QueryDict) -> (int, dict):
    '''
    Аутентификация пользователя

    Args:
        data: данные пользователя

    Returns:
        Кортеж из статуса и словаря данных
    '''

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
    '''
    Получение данных пользователя
    Args:
        user: пользователь

    Returns:
        Кортеж из статуса и словаря данных
    '''

    logger.info(
        msg=f'Получение данных пользователя {user}',
    )
    data = CustomUserSerializer(
        instance=user,
    ).data

    logger.info(
        msg=f'Данные пользователя {user} успешно получены: {data}',
    )
    return generate_response(
        status_code=200,
        data=data,
    )


def update(user: CustomUser, data: QueryDict) -> (int, dict):
    '''
    Обновление данных пользователя

    Args:
        user: пользователь
        data: данные пользователя

    Returns:
        Кортеж из статуса и словаря данных
    '''

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
            msg=f'Невалидные данные для обновления '
                f'пользователя {user} {user_data}: {serializer.errors}',
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
            msg=f'Возникла ошибка при попытке обновить '
                f'данные пользователя {user}: {user_data}',
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


def remove(user: CustomUser) -> (int, dict):
    '''
    Удаление пользователя
    Args:
        user: пользователь

    Returns:
        Кортеж из статуса и словаря данных
    '''

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


def send_email_by_type(user: CustomUser, get_url_func: Callable, email_type: str) -> int:
    '''
    Отправка письма по типу

    Args:
        user: пользователь
        get_url_func: функция для создания ссылки
        email_type: тип письма

    Returns:
        Статус
    '''

    logger.info(
        msg=f'Получение данных для формирования текста '
            f'письма {email_type} пользователю {user}',
    )

    url_hash = str(uuid.uuid4())
    user.url_hash = url_hash

    try:
        user.save()
    except Exception as exc:
        logger.error(
            msg=f'Не удалось получить данные для '
                f'формирования текста письма {email_type} пользователю {user}',
            exc_info=True,
        )
        return 500

    url = get_url_func(reverse(email_type, args=(user.url_hash,)))
    mail_data = {
        'url': url,
    }

    logger.info(
        msg=f'Данные для формирования текста письма {email_type} '
            f'пользователю {user} получены: {mail_data}',
    )

    email = Email(
        email_type=email_type,
        mail_data=mail_data,
        recipient=user,
    )
    status = email.send()
    return status


def confirm_email(url_hash: str) -> (int, dict):
    '''
    Подтверждение email

    Args:
        url_hash: хэш

    Returns:
        Кортеж из статуса и словаря данных
    '''

    logger.info(
        msg=f'Подтверждение email пользователя с хэшем {url_hash}',
    )

    try:
        user = CustomUser.objects.filter(
            url_hash=url_hash,
        ).first()
    except Exception as exc:
        logger.error(
            msg=f'Ошибка при поиске пользователя с хэшем '
                f'{url_hash} для подтверждения email',
            exc_info=True,
        )
        return generate_response(
            status_code=500,
        )

    if user is None:
        logger.error(
            msg=f'Пользователь с хэшем {url_hash} для подтверждения email не найден',
        )
        return generate_response(
            status_code=404,
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


def password_restore(url_hash: str, data: QueryDict) -> (int, dict):
    '''
    Восстановление пароля

    Args:
        url_hash: хэш
        data: данные для восстановления

    Returns:
        Кортеж из статуса и словаря данных
    '''

    logger.info(
        msg=f'Сброс пароля пользователя с хэшем {url_hash}',
    )

    try:
        user = CustomUser.objects.filter(
            url_hash=url_hash,
        ).first()
    except Exception as exc:
        logger.error(
            msg=f'Ошибка при поиске пользователя с хэшем {url_hash} для сброса пароля',
            exc_info=True,
        )
        return generate_response(
            status_code=500,
        )

    if user is None:
        logger.error(
            msg=f'Пользователь с хэшем {url_hash} для сброса пароля не найден',
        )
        return generate_response(
            status_code=404,
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
            msg=f'Невалидные данные для сброса пароля '
                f'пользователя {user} {user_data}: {serializer.errors}',
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
            msg=f'Возникла ошибка при сбросe пароля '
                f'пользователя {user} {user_data}: {serializer.errors}',
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


def password_restore_request(data: QueryDict, get_url_func: Callable) -> (int, dict):
    '''
    Запрос на восстановление пароля

    Args:
        data: данные для запроса
        get_url_func: функция для создания ссылки

    Returns:
        Кортеж из статуса и словаря данных
    '''

    email = data.get('email')
    logger.info(
        msg=f'Запрос на сброс пароля пользователя {email}',
    )

    serializer = PasswordRestoreSerializer(
        data=data,
    )
    if not serializer.is_valid():
        logger.error(
            msg=f'Невалидные данные для запроса на сброс пароля '
                f'пользователя {email}: {serializer.errors}',
        )
        return generate_response(
            status_code=400,
        )

    try:
        user = CustomUser.objects.filter(
            email=email,
        ).first()
    except Exception as exc:
        logger.error(
            msg=f'Ошибка при поиске пользователя с email {email} '
                f'для запроса на сброс пароля',
            exc_info=True,
        )
        return generate_response(
            status_code=500,
        )

    if user is None:
        logger.error(
            msg=f'Пользователь с email {email} для запроса на сброс пароля не найден',
        )
        return generate_response(
            status_code=406,
        )

    status_code = send_email_by_type(
        user=user,
        email_type=PASSWORD_RESTORE,
        get_url_func=get_url_func,
    )

    if status_code != 200:
        logger.error(
            msg=f'Запрос на сброс пароля пользователя {email} не прошел',
        )
    else:
        logger.info(
            msg=f'Запрос на сброс пароля пользователя {email} прошел успешно',
        )
    return generate_response(
        status_code=status_code,
    )
