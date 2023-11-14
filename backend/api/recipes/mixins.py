from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet


class IngredientAndTagMixinViewSet(mixins.ListModelMixin,
                                   mixins.RetrieveModelMixin,
                                   GenericViewSet):
    pass
