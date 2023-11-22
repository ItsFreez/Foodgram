from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


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


class Recipe(models.Model):
    name = models.CharField(
        'Название',
        max_length=settings.MAXL_RECIPE_NAME,
        help_text='Обязательное. Укажите название для рецепта.'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/images/',
        help_text='Обязательное. Добавьте изображение рецепта.'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
        help_text='Обязательное. Укажите теги для рецепта.'
    )
    text = models.TextField(
        'Описание',
        help_text='Обязательное. Опишите рецепт приготовления.'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredientsRelated',
        verbose_name='Ингредиенты',
        help_text='Обязательное. Укажите ингредиенты для рецепта.'
    )
    cooking_time = models.SmallIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(1)],
        help_text='Обязательное. Укажите время приготовления в минутах.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        help_text='Обязательное. Укажите автора для рецепта.'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredientsRelated(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_list',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Ингредиент'
    )
    amount = models.SmallIntegerField(
        'Количество ингредиента',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        ordering = ('recipe', 'ingredient',)
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            ),
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('user', 'recipe',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_favorite'
            ),
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='buyers',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'корзина покупок'
        verbose_name_plural = 'Корзины покупок'
        ordering = ('user', 'recipe',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_shopping_cart'
            ),
        ]
