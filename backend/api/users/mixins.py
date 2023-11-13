from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet


class UserMixinViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       GenericViewSet):
    pass
