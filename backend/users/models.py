from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class User(AbstractUser):
    """Модель для пользователей."""

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        'Имя пользователя',
        max_length=settings.MAXL_USERS_ATTRS,
        unique=True,
        help_text='Обязательное. Не более 150 символов.',
        validators=(username_validator,),
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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель для подписок на пользователей."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Пользователь'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followings',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('user', 'following',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='unique_user_following'
            ),
            models.CheckConstraint(
                name='user_following_different',
                check=~models.Q(user=models.F('following')),
            ),
        ]
