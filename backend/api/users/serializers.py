from django.conf import settings
from rest_framework import serializers

from users.models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        user_obj = self.context['request'].user
        if user_obj.is_authenticated():
            return Follow.objects.filter(user=user_obj, following=obj).exists()
        else:
            return False


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        required=True,
        max_length=settings.MAXL_USERS_ATTRS
    )
    current_password = serializers.CharField(
        required=True,
        max_length=settings.MAXL_USERS_ATTRS
    )
