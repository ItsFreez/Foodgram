from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.recipes.serializers import RecipeShortSerializer
from users.models import Follow

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        user_obj = self.context['request'].user
        if user_obj.is_authenticated:
            return Follow.objects.filter(user=user_obj, following=obj).exists()
        return False


class UserForFollowSerializer(UserSerializer):
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


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        required=True,
        max_length=settings.MAXL_USERS_ATTRS
    )
    current_password = serializers.CharField(
        required=True,
        max_length=settings.MAXL_USERS_ATTRS
    )


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    following = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Follow
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following',),
                message='Подписка уже оформлена!'
            )
        ]

    def validate_following(self, following):
        if following == self.context['request'].user.id:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!'
            )
        return following

    def to_representation(self, instance):
        user_obj = User.objects.get(id=instance.following.id)
        return UserForFollowSerializer(user_obj, context=self.context).data
