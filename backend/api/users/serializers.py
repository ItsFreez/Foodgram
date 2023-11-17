from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers

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
        limit = request.GET.get('recipes_limit')
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
