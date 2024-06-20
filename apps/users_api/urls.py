from django.urls import path

from users_api.api import (
    RegisterView,
    AuthView,
    CustomUserView,
    ConfirmEmailView,
    PasswordRestoreRequestView,
    PasswordRestoreView,
)

from utils.constants import (
    CONFIRM_EMAIL,
    PASSWORD_RESTORE,
)


urlpatterns = [
    path(
        'register/',
        RegisterView.as_view(),
        name='register',
    ),
    path(
        'auth/',
        AuthView.as_view(),
        name='auth',
    ),
    path(
        'confirm/email/<str:url_hash>/',
        ConfirmEmailView.as_view(),
        name=CONFIRM_EMAIL,
    ),
    path(
        'password/restore/request/',
        PasswordRestoreRequestView.as_view(),
        name='password_restore_request',
    ),
    path(
        'password/restore/<str:url_hash>/',
        PasswordRestoreView.as_view(),
        name=PASSWORD_RESTORE,
    ),
    path(
        '',
        CustomUserView.as_view(),
        name='user_api'
    ),
]
