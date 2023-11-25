import datetime

from django.db.models import Exists, OuterRef, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.common.paginators import PagePagination
from api.recipes.filters import IngredientFilter, RecipeFilter
from api.recipes.permissions import IsAdminOrOwnerOrReadOnly
from api.recipes.serializers import (FavoriteSerializer, IngredientSerializer,
                                     RecipeReadSerializer,
                                     RecipeWriteSerializer,
                                     ShoppingCartSerializer, TagSerializer)
from recipes.models import (Favorite, Ingredient, Recipe,
                            RecipeIngredientsRelated, Tag, ShoppingCart)


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для работы с объектами Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для работы с объектами Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    """Вьюсет для работы с объектами Recipe."""

    permission_classes = (IsAdminOrOwnerOrReadOnly,)
    pagination_class = PagePagination
    http_method_names = ('get', 'post', 'patch', 'delete')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        if self.request.user.is_authenticated:
            is_favorited = self.request.user.favorites.filter(
                recipe=OuterRef('pk')
            )
            is_in_shopping_cart = self.request.user.shopping_cart.filter(
                recipe=OuterRef('pk')
            )
            return Recipe.objects.annotate(
                is_favorited=Exists(is_favorited),
                is_in_shopping_cart=Exists(is_in_shopping_cart)
            ).order_by('-pub_date')
        return Recipe.objects.all()

    def get_serializer_class(self):
        """Возвращает сериализатор в зависимости от метода запроса."""
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @staticmethod
    def add_recipe(work_serializer, pk, request):
        """Добавляет рецепт в model указанного serializer."""
        serializer = work_serializer(
            context={'request': request},
            data={'user': request.user.id, 'recipe': pk}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_recipe(model, user, pk):
        """Удаляет рецепт из указанного объекта model."""
        recipe = get_object_or_404(Recipe, id=pk)
        deleted_obj = model.objects.filter(user=user, recipe=recipe).delete()
        if deleted_obj == 0:
            return Response(
                {'errors': ['Рецепта нет в этом списке!']},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('post', 'delete'),
        detail=True,
        url_path='favorite',
        serializer_class=FavoriteSerializer,
        permission_classes=(IsAuthenticated,)
    )
    def delete_post_favorite(self, request, pk):
        """Добавляет/удаляет объект Recipe из избранного."""
        if request.method in ['DELETE']:
            return self.delete_recipe(Favorite, request.user, pk)
        return self.add_recipe(self.get_serializer_class, pk, self.request)

    @action(
        methods=('post', 'delete'),
        detail=True,
        url_path='shopping_cart',
        serializer_class=ShoppingCartSerializer,
        permission_classes=(IsAuthenticated,)
    )
    def delete_post_shopping_cart(self, request, pk):
        """Добавляет/удаляет объект Recipe из списка покупок."""
        if request.method in ['DELETE']:
            return self.delete_recipe(ShoppingCart, request.user, pk)
        return self.add_recipe(self.get_serializer_class, pk, self.request)

    @staticmethod
    def create_file_shopping_cart(user, ingredients):
        today = datetime.datetime.today()
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

    @action(
        methods=('get',),
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def get_file_shopping_cart(self, request):
        """Формирует и отправляет файл с ингредиентами объекта Recipe."""
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = RecipeIngredientsRelated.objects.filter(
            recipe__shopping_cart__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).order_by('ingredient__name').annotate(amount=Sum('amount'))
        return self.create_file_shopping_cart(user, ingredients)
