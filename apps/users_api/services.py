from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

from users_api.models import CustomUser


def authenticate_user(request) -> (int, dict):
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(
        email=email,
        password=password,
    )
    if user is None:
        return 401, {
            'error': 'Невалидные данные',
        }
    email = user.email
    try:
        token = Token.objects.filter(
            user=user,
        ).first()
    except Exception as exc:
        print(f'Ошибка при попытке получить токен пользователя {email}: {exc}')
        return 500, {
            'error': 'Ошибка при поиске токена пользователя'
        }
    if token is None:
        return 404, {
            'error': 'Токен для пользователя не найден',
        }
    return 200, {
        'token': token.key,
        'email': email,
    }
