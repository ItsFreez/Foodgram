from django.conf import settings
from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'
        write_only_fields = ('password',)


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        required=True,
        max_length=settings.MAXL_USERS_ATTRS
    )
    current_password = serializers.CharField(
        required=True,
        max_length=settings.MAXL_USERS_ATTRS
    )
