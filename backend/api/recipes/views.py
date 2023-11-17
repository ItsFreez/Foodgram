from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.recipes.permissions import IsAdminOrOwnerOrReadOnly
from api.recipes.serializers import (IngredientSerializer,
                                     RecipeReadSerializer,
                                     RecipeWriteSerializer,
                                     RecipeShortSerializer,
                                     TagSerializer)
from recipes.models import Favorite, Ingredient, Recipe, Tag, ShoppingCart


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeWriteSerializer
    permission_classes = (IsAdminOrOwnerOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return super().get_serializer_class()

    def add_recipe(self, model, user, recipe):
        obj, created = model.objects.get_or_create(user=user, recipe=recipe)
        if not created:
            return Response(
                {'errors': ['Рецепт уже добавлен в список!']},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, model, user, recipe):
        obj = model.objects.filter(user=user, recipe=recipe)
        if not obj.exists():
            return Response(
                {'errors': ['Рецепта нет в этом списке!']},
                status=status.HTTP_400_BAD_REQUEST
            )
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def delete_post_favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method in ['DELETE']:
            return self.delete_recipe(Favorite, request.user, recipe)
        return self.add_recipe(Favorite, request.user, recipe)

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def delete_post_shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method in ['DELETE']:
            return self.delete_recipe(ShoppingCart, request.user, recipe)
        return self.add_recipe(ShoppingCart, request.user, recipe)
