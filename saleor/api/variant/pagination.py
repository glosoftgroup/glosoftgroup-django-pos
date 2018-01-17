from rest_framework.response import Response
from rest_framework.pagination import (
    LimitOffsetPagination,
    PageNumberPagination,
)

from rest_framework import pagination


class PostLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 10


class PostPageNumberPagination(PageNumberPagination):
    page_size = 2


class PostLimitOffsetPagination(pagination.PageNumberPagination, LimitOffsetPagination):

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })

