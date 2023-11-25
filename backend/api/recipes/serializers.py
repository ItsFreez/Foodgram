from django.db import transaction
from django.db.models import F
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from api.common.serializers import Base64ImageField, RecipeShortSerializer
from api.users.serializers import UserSerializer
from recipes.models import (Favorite, Ingredient, Recipe,
                            RecipeIngredientsRelated, ShoppingCart, Tag)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор объектов Tag."""

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор объектов Ingredient."""

    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('name', 'measurement_unit')


class IngredientForRecipeWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор промежуточной таблицы Recipe и Ingredient
    для запросов по записи/изменению ингредиентов и их количества.
    """

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredientsRelated
        fields = ('id', 'amount')


class BaseRecipeSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для объектов Recipe."""

    class Meta:
        model = Recipe
        exclude = ('pub_date',)


class RecipeReadSerializer(BaseRecipeSerializer):
    """Сериализатор только для чтения объектов Recipe."""

    image = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    author = UserSerializer()
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def get_ingredients(self, obj):
        ingredients = obj.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipes__amount')
        )
        return ingredients


class RecipeWriteSerializer(BaseRecipeSerializer):
    """Сериализатор для записи/изменения объектов Recipe."""

    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientForRecipeWriteSerializer(many=True)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate(self, attrs):
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        if ingredients is None:
            raise ValidationError('Пропущено обязательное поле ingredients.')
        if tags is None:
            raise ValidationError('Пропущено обязательное поле tags.')
        if len(ingredients) == 0:
            raise ValidationError('Выберите хотя бы один ингредиент.')
        if len(tags) == 0:
            raise ValidationError('Выберите хотя бы один тег.')
        ingredients_list = []
        for item in ingredients:
            if item.get('id') in ingredients_list:
                raise ValidationError(
                    'Ингредиенты не должны быть повторяться.'
                )
            ingredients_list.append(item.get('id'))
        unique_tags = set(tags)
        if len(unique_tags) != len(tags):
            raise ValidationError('Выбранные теги не должны повторяться.')
        return attrs

    @staticmethod
    def save_ingredients_relations(recipe, ingredients):
        ingredient_list = []
        for item in ingredients:
            ingredient_list.append(
                RecipeIngredientsRelated(
                    recipe=recipe, ingredient=item['id'], amount=item['amount']
                )
            )
        RecipeIngredientsRelated.objects.bulk_create(ingredient_list)

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.save_ingredients_relations(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.save_ingredients_relations(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное!'
            )
        ]

    def to_representation(self, instance):
        recipe_obj = Recipe.objects.get(id=instance.recipe.id)
        return RecipeShortSerializer(recipe_obj, context=self.context).data


class ShoppingCartSerializer(FavoriteSerializer):

    class Meta:
        model = ShoppingCart
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в список покупок!'
            )
        ]
