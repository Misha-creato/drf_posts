from django.urls import path
from users_api.api import (
    RegisterView,
    AuthView,
    CustomUserView,
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
        '',
        CustomUserView.as_view(),
        name='user_api'
    ),
]
