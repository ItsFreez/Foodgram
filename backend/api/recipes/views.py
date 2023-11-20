import datetime

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.recipes.filters import RecipeFilter
from api.recipes.permissions import IsAdminOrOwnerOrReadOnly
from api.recipes.serializers import (IngredientSerializer,
                                     RecipeReadSerializer,
                                     RecipeWriteSerializer,
                                     RecipeShortSerializer,
                                     TagSerializer)
from recipes.models import (Favorite, Ingredient, Recipe,
                            RecipeIngredientsRelated, Tag, ShoppingCart)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeWriteSerializer
    permission_classes = (IsAdminOrOwnerOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

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

    @action(
        methods=['get'],
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def get_pdf_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = RecipeIngredientsRelated.objects.filter(
            recipe__buyers__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).order_by('ingredients__name').annotate(amount=Sum('amount'))
        today = datetime.today()
        shopping_cart = (
            f'Список покупок для {user.get_full_name()}\n'
            f'От {today:%d.%m.%Y}\n\n'
        )
        for ingredient in ingredients:
            shopping_cart += (
                f'{ingredient["ingredient__name"]} - {ingredient["amount"]} '
                f'{ingredient["ingredient__measurement_unit"]}\n'
            )
        shopping_cart += '\nFoodgram - Ваш Продуктовый помощник.'
        file = f'Shopping_cart_for_{user.username}.txt'
        response = HttpResponse(
            shopping_cart,
            content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={file}'
        return response
