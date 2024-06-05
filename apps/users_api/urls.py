from django.urls import path
from users_api.api import (
    RegisterView,
    LoginView,
    CustomUserView,
)


urlpatterns = [
    path(
        'register/',
        RegisterView.as_view(),
    ),
    path(
        'login/',
        LoginView.as_view(),
    ),
    path(
        '',
        CustomUserView.as_view(),
    ),
]
