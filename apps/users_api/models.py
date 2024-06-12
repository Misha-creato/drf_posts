import io
import uuid
from datetime import timedelta
from PIL import Image

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.utils import timezone


AVATAR_SIZE_WIDTH = 100
AVATAR_SIZE_HEIGHT = 100


class CustomUserManager(BaseUserManager):
    def create_user(self, email: str, password: str, **extra_fields):
        if not email:
            raise ValueError('Требуется электронная почта')
        email = self.normalize_email(email=email)
        user = self.model(email=email, **extra_fields)
        user.set_password(raw_password=password)
        user.save()
        return user

    def create_superuser(self, email: str, password: str):
        return self.create_user(
            email=email,
            password=password,
            is_superuser=True,
            is_staff=True,
        )


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True,
    )
    avatar = models.ImageField(
        default='avatars/default.jpeg',
        verbose_name='Аватар',
        upload_to='avatars',
    )
    thumbnail = models.ImageField(
        default='thumbnails/default.jpeg',
        verbose_name='Миниатюра',
        upload_to='thumbnails',
    )
    is_superuser = models.BooleanField(
        verbose_name='Статус суперпользователя',
        default=False
    )
    is_staff = models.BooleanField(
        verbose_name='Статус персонала',
        default=False,
    )
    is_active = models.BooleanField(
        verbose_name='Статус активности',
        default=True,
    )
    email_confirmed = models.BooleanField(
        verbose_name='Адрес электронной почты подтвержден',
        default=False,
    )
    url_hash = models.CharField(
        verbose_name='Хэш',
        max_length=128,
        null=True,
        blank=True,
    )
    date_joined = models.DateTimeField(
        verbose_name='Дата регистрации',
        auto_now_add=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __make_thumbnail(self):
        with Image.open(self.avatar) as img:
            if img.mode in ('RGBA', 'LA'):
                img = img.convert('RGB')

            img.thumbnail((AVATAR_SIZE_WIDTH, AVATAR_SIZE_HEIGHT))
            thumb = io.BytesIO()
            img.save(thumb, format='JPEG', quality=90)

            self.thumbnail = SimpleUploadedFile(self.avatar.name, thumb.getvalue())

    def save(self, *args, **kwargs):
        if self.avatar and self.pk:
            old_avatar = CustomUser.objects.get(pk=self.pk).avatar
            if self.avatar != old_avatar:
                self.__make_thumbnail()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class CustomToken(models.Model):
    user = models.OneToOneField(
        verbose_name='Пользователь',
        to=settings.AUTH_USER_MODEL,
        related_name='auth_token',
        on_delete=models.CASCADE,
    )
    key = models.CharField(
        verbose_name='Ключ',
        max_length=64,
        primary_key=True,
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
    )
    expires_at = models.DateTimeField(
        verbose_name='Дата истечения',
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.__generate_key()
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        return super().save(*args, **kwargs)

    def __generate_key(self):
        return str(uuid.uuid4())

    def is_expired(self):
        return self.expires_at <= timezone.now()

    def __str__(self):
        return self.user.email

    class Meta:
        db_table = 'custom_token'
        verbose_name = 'Токен'
        verbose_name_plural = 'Токены'
