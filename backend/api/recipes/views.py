from rest_framework.permissions import AllowAny

from api.recipes.mixins import IngredientAndTagMixinViewSet
from api.recipes.serializers import IngredientSerializer, TagSerializer
from recipes.models import Ingredient, Tag


class IngredientViewSet(IngredientAndTagMixinViewSet):
    queryset = Ingredient
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)


class TagViewSet(IngredientAndTagMixinViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
