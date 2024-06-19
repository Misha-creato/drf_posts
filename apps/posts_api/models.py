import uuid

from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Post(models.Model):
    author = models.ForeignKey(
        to=User,
        related_name='posts',
        on_delete=models.CASCADE,
    )
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=256,
    )
    description = models.TextField(
        verbose_name='Описание',
        null=True,
        blank=True,
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='images/',
        null=True,
        blank=True,
    )
    hidden = models.BooleanField(
        verbose_name='Скрыт',
        default=False,
    )
    slug = models.CharField(
        verbose_name='Слаг',
        max_length=256,
        unique=True,
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
    )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = str(uuid.uuid4())
        return super().save()

    class Meta:
        ordering = [
            '-created_at',
        ]
        db_table = 'posts'
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
