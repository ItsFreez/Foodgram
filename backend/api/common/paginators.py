from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class PagePagination(PageNumberPagination):
    """Кастомный пагинатор с ограничением объектов через параметр limit."""

    page_size_query_param = 'limit'
    page_size = settings.DEFAULT_PAGE_SIZE
