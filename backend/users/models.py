from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models


class CustomUser(AbstractUser):
    """Переопределяем модель пользователя, добавив/изменив необходимые поля"""

    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        null=False,
        validators=[validators.RegexValidator(
            r'^[\w.@+-]+\Z',
            'Недопустимые символы в логине!'
        )],
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=254,
        unique=True,
        null=False,
    )
    first_name = models.CharField('Имя', max_length=150, blank=False)
    last_name = models.CharField('Фамилия', max_length=150, blank=False)
    password = models.CharField('Пароль', max_length=150, blank=False)

    @property
    def is_subscribed(self):
        return False

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('date_joined',)

    def __str__(self):
        return self.username
