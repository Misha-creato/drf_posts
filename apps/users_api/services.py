import uuid

from django.contrib.auth import authenticate
from django.http.request import QueryDict
from django.urls import reverse

from config.settings import (
    SITE_PROTOCOL,
    SITE_DOMAIN,
)
from notifications.services import SendMails
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


def create_user(data: QueryDict) -> (int, dict):
    user_data = get_log_user_data(
        user_data=data.dict(),
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
    send_confirm_email(user=user)
    return generate_response(
        status_code=200,
    )


def authenticate_user(data: QueryDict) -> (int, dict):
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

    if token is None:
        logger.error(
            msg=f'Токен пользователя {email} не найден',
        )
        return generate_response(
            status_code=404,
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


def get_user(user: CustomUser) -> (int, dict):
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


def update_user(user: CustomUser, data: QueryDict) -> (int, dict):
    user_data = get_log_user_data(
        user_data=data.dict(),
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


def delete_user(user: CustomUser) -> (int, dict):
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


def set_url_hash(user: CustomUser) -> int:
    logger.info(
        msg=f'Установка хэша для пользователя {user}',
    )
    url_hash = str(uuid.uuid4())
    user.url_hash = url_hash

    try:
        user.save()
    except Exception as exc:
        logger.error(
            msg=f'Не удалось установить хэш для пользователя {user}',
            exc_info=True,
        )
        return 500

    logger.info(
        msg=f'Хэш для пользователя {user} установлен',
    )
    return 200


def get_mail_data(user: CustomUser, email_type: str) -> (int, dict):
    logger.info(
        msg=f'Получение данных для формирования текста письма {email_type} пользователю {user}',
    )
    status = set_url_hash(
        user=user,
    )
    if status != 200:
        logger.error(
            msg=f'Не удалось получить данные для формирования текста письма {email_type} \
            пользователю {user}',
        )
        return status, {}

    path = reverse('confirm_email', args=(user.url_hash,))
    url = f'{SITE_PROTOCOL}://{SITE_DOMAIN}{path}'
    mail_data = {
        'url': url,
    }

    logger.info(
        msg=f'Данные для формирования текста письма {email_type} \
        пользователю {user} получены: {mail_data}',
    )
    return 200, mail_data


def send_confirm_email(user: CustomUser) -> None:
    email_type = 'confirm_email'
    status, mail_data = get_mail_data(
        user=user,
        email_type=email_type,
    )

    if status != 200:
        return generate_response(
            status_code=status,
        )

    send_mails = SendMails(email_type=email_type, mail_data=mail_data, recipient=user)
    status = send_mails.send_mail_to_user()
    # return generate_response(
    #     status_code=status,
    # )
