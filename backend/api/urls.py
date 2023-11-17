from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.recipes.views import IngredientViewSet, RecipeViewSet, TagViewSet
from api.users.views import UserViewSet

router = DefaultRouter
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls'))
]
