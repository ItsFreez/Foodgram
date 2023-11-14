from django.conf import settings
from django.db import models


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=settings.MAXL_TAG_ATTRS,
        unique=True,
        help_text='Обязательное. Не более 10 символов.',
        error_messages={
            'unique': 'Данное название тега уже занято!',
        }
    )
    color = models.CharField(
        'Цветовой код',
        max_length=settings.MAXL_TAG_ATTRS,
        unique=True,
        help_text='Обязательное. Укажите шестнадцатеричный код цвета.',
        error_messages={
            'unique': 'Данный код уже используется!',
        }
    )
    slug = models.SlugField(
        'Слаг',
        max_length=settings.MAXL_TAG_ATTRS,
        unique=True,
        help_text='Обязательное. Укажите слаг для тега. Не более 10 символов.',
        error_messages={
            'unique': 'Данный слаг уже используется!',
        }
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=settings.MAXL_INGRED_NAME,
        help_text='Обязательное. Укажите название ингредиента.'
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=settings.MAXL_INGRED_UNIT,
        help_text='Обязательное. Укажите единицу измерения для ингредиента.'
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name', 'measurement_unit',)

    def __str__(self):
        return self.name
