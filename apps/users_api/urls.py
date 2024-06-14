from django.urls import path
from users_api.api import (
    RegisterView,
    AuthView,
    CustomUserView,
    ConfirmEmailView,
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
        'confirm/email/<str:url_hash>',
        ConfirmEmailView.as_view(),
        name='confirm_email',
    ),
    path(
        '',
        CustomUserView.as_view(),
        name='user_api'
    ),
]
