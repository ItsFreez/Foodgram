import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.users.serializers import UserSerializer
from recipes.models import (Favorite, Ingredient, Recipe,
                            RecipeIngredientsRelated, ShoppingCart, Tag)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientForRecipeReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredientsRelated
        fields = ('ingredient', 'amount')


class IngredientForRecipeWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = RecipeIngredientsRelated
        fields = ('amount',)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class BaseRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeReadSerializer(BaseRecipeSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientForRecipeReadSerializer(many=True)
    author = UserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        user_obj = self.context['request'].user
        if user_obj.is_authenticated():
            return Favorite.objects.filter(user=user_obj, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user_obj = self.context['request'].user
        if user_obj.is_authenticated():
            return ShoppingCart.objects.filter(
                user=user_obj,
                recipe=obj
            ).exists()
        return False


class RecipeWriteSerializer(BaseRecipeSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientForRecipeWriteSerializer(many=True)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_ingredients(self, ingredients):
        ingredients_list = []
        for value in ingredients:
            ingredient = get_object_or_404(Ingredient, id=value['id'])
            if ingredient in ingredients_list:
                raise ValidationError(
                    'Ингредиенты не должны быть повторяться.'
                )
            ingredients_list.append(ingredient)
        return ingredients

    def validate_tags(self, tags):
        unique_tags = set(tags)
        if len(unique_tags) != len(tags):
            raise ValidationError('Выбранные теги не должны повторяться.')
        return tags
