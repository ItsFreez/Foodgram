from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.common.serializers import RecipeShortSerializer
from users.models import Follow

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор объектов User."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.subscriptions.filter(
                    following=obj
                ).exists())


class UserForFollowSerializer(UserSerializer):
    """Расширенный сериализатор объектов User с полями для рецептов."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, user):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = user.recipes.all()
        if limit is not None:
            recipes = recipes[:int(limit)]
        return RecipeShortSerializer(recipes, many=True).data

    def get_recipes_count(self, user):
        return user.recipes.count()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count',)


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с подписками пользователей."""

    class Meta:
        model = Follow
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Подписка уже оформлена!'
            )
        ]

    def validate_following(self, following):
        if following == self.context['request'].user:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!'
            )
        return following

    def to_representation(self, instance):
        user_obj = User.objects.get(id=instance.following.id)
        return UserForFollowSerializer(user_obj, context=self.context).data
