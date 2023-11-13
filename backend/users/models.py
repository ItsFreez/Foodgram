from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from users.validators import ban_name_me


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        'Имя пользователя',
        max_length=settings.MAXL_USERS_ATTRS,
        unique=True,
        help_text='Обязательное. Не более 150 символов.',
        validators=[username_validator, ban_name_me],
        error_messages={
            'unique': 'Пользователь с таким username уже существует!',
        }
    )
    email = models.EmailField(
        'Адрес электронной почты',
        max_length=settings.MAXL_EMAIL,
        unique=True,
        help_text='Обязательное. Не более 254 символов.',
        error_messages={
            'unique': 'Пользователь с таким email уже существует!',
        }
    )
    first_name = models.CharField(
        'Имя',
        max_length=settings.MAXL_USERS_ATTRS,
        help_text='Обязательное. Не более 150 символов.'
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.MAXL_USERS_ATTRS,
        help_text='Обязательное. Не более 150 символов.'
    )
    password = models.CharField(
        'Пароль',
        max_length=settings.MAXL_USERS_ATTRS,
        help_text='Обязательное. Не более 150 символов.'
        )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username
