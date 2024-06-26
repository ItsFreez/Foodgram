import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import Recipe


class Base64ImageField(serializers.ImageField):
    """Кастомное поле изображений для преобразования из формата base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор объектов Recipe для получения краткого описания."""

    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None
