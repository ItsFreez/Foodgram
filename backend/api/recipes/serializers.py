import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

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


class IngredientForRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredientsRelated
        fields = ("id", "name", "measurement_unit", "amount")


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeReadSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(many=True)
    ingredients = IngredientForRecipeSerializer(many=True)
    author = UserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

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
