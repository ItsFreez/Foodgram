from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser import views
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.common.paginators import PagePagination
from api.users.serializers import FollowSerializer, UserForFollowSerializer
from users.models import Follow

User = get_user_model()


class UserViewSet(views.UserViewSet):
    """Вьюсет для работы с объектами User."""

    pagination_class = PagePagination

    @action(
        methods=('post', 'delete'),
        detail=True,
        url_path='subscribe',
        permission_classes=(IsAuthenticated,),
        serializer_class=FollowSerializer
    )
    def delete_post_subscribe(self, request, pk):
        """Оформляет/отменяет подписку на другого пользователя."""
        following = get_object_or_404(User, id=pk)
        if request.method in ['DELETE']:
            deleted_obj = Follow.objects.filter(
                user=request.user, following=following
            ).delete()
            if deleted_obj == 0:
                return Response(
                    {'errors': ['Вы не подписаны на этого пользователя!']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            serializer = self.get_serializer(
                context={'request': request},
                data={'user': request.user, 'following': following}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(user=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=('get',),
        detail=False,
        url_path='subscriptions',
        permission_classes=(IsAuthenticated,),
        serializer_class=UserForFollowSerializer
    )
    def get_all_subscriptions(self, request):
        """Получить список всех подписок пользователя."""
        queryset = User.objects.filter(followings__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
