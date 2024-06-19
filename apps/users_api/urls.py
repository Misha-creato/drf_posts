from django.urls import path
from users_api.api import (
    RegisterView,
    AuthView,
    CustomUserView,
    ConfirmEmailView,
    PasswordResetRequestView,
    PasswordResetView,
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
        name='confirm_email',
    ),
    path(
        'password/reset/request/',
        PasswordResetRequestView.as_view(),
        name='password_reset_request',
    ),
    path(
        'password/reset/<str:url_hash>/',
        PasswordResetView.as_view(),
        name='password_reset',
    ),
    path(
        '',
        CustomUserView.as_view(),
        name='user_api'
    ),
]
