import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.users.serializers import UserSerializer
from recipes.models import (Favorite, Ingredient, Recipe,
                            RecipeIngredientsRelated, ShoppingCart, Tag)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientForRecipeWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = RecipeIngredientsRelated
        fields = ('amount',)


class IngredientForRecipeReadSerializer(IngredientForRecipeWriteSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )


class BaseRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        exclude = ('pub_date',)


class RecipeReadSerializer(BaseRecipeSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientForRecipeReadSerializer(many=True)
    author = UserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        user_obj = self.context['request'].user
        if user_obj.is_authenticated:
            return Favorite.objects.filter(user=user_obj, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user_obj = self.context['request'].user
        if user_obj.is_authenticated:
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
        for item in ingredients:
            ingredient = get_object_or_404(Ingredient, id=item.get('id'))
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

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.save_ingredients_relations(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.save_ingredients_relations(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data

    def save_ingredients_relations(self, recipe, ingredients):
        for item in ingredients:
            ingredient = get_object_or_404(Ingredient, id=item.get('id'))
            RecipeIngredientsRelated.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=item.get('amount')
            )


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
