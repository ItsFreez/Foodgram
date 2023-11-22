from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.users.serializers import UserSerializer
from core.serializers import Base64ImageField
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


class IngredientForRecipeWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredientsRelated
        fields = ('id', 'amount',)


class BaseRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        exclude = ('pub_date',)


class RecipeReadSerializer(BaseRecipeSerializer):
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    author = UserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        ingredients = obj.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipes__amount')
        )
        return ingredients

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
