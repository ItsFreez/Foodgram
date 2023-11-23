from rest_framework.pagination import PageNumberPagination


class PagePagination(PageNumberPagination):
    """Кастомный пагинатор с ограничением объектов через параметр limit."""

    page_size_query_param = 'limit'
    page_size = 6
