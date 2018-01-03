from rest_framework.pagination import (
    LimitOffsetPagination,
    PageNumberPagination,
)


class PostLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 100
    max_limit = 100


class PostPageNumberPagination(PageNumberPagination):
    page_size =  2