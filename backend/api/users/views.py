from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.users.mixins import UserMixinViewSet
from api.users.serializers import (ChangePasswordSerializer, FollowSerializer,
                                   UserForFollowSerializer, UserSerializer)
from users.models import Follow

User = get_user_model()


class UserViewSet(UserMixinViewSet):
    """Вьюсет для работы с объектами User."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        """Создает объект пользователя и формирует пароль."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data.pop('password')
        username = serializer.validated_data['username']
        self.perform_create(serializer)
        user_obj = get_object_or_404(User, username=username)
        user_obj.set_password(password)
        user_obj.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @action(
        methods=['GET'],
        detail=False,
        url_path='me',
        permission_classes=(IsAuthenticated,),
        serializer_class=UserSerializer
    )
    def get_userprofile_for_owner(self, request):
        """Возвращает описание текущего пользователя."""
        user_obj = get_object_or_404(
            User,
            username=request.user.username
        )
        serializer = self.get_serializer(user_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['POST'],
        detail=False,
        url_path='set_password',
        permission_classes=(IsAuthenticated,),
        serializer_class=ChangePasswordSerializer
    )
    def post_new_password(self, request):
        """Проверяет и сохраняет новый пароль для пользователя."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data['new_password']
        current_password = serializer.validated_data['current_password']
        user_obj = get_object_or_404(
            User,
            username=request.user.username
        )
        if not user_obj.check_password(current_password):
            return Response(
                {'current_password': ['Указан неверный пароль!']},
                status=status.HTTP_400_BAD_REQUEST
            )
        user_obj.set_password(new_password)
        user_obj.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='subscribe',
        permission_classes=(IsAuthenticated,),
        serializer_class=FollowSerializer
    )
    def delete_post_subscribe(self, request, pk):
        """Оформляет/отменяет подписку на другого пользователя."""
        following = get_object_or_404(User, id=pk)
        if request.method in ['DELETE']:
            obj = Follow.objects.filter(user=request.user, following=following)
            if not obj.exists():
                return Response(
                    {'errors': ['Вы не подписаны на этого пользователя!']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            serializer = self.get_serializer(
                data={**request.data, 'following': pk}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(user=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=['get'],
        detail=False,
        url_path='subscriptions',
        permission_classes=(IsAuthenticated,),
        serializer_class=UserForFollowSerializer
    )
    def get_all_subscriptions(self, request):
        """Получить список всех подписок пользователя."""
        queryset = User.objects.filter(followings__user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
