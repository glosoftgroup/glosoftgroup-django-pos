from rest_framework.response import Response

import random
from rest_framework.decorators import api_view
from .serializers import (
    OrderNumberSerializer,
     )


class Comment(object):
    def __init__(self, number):
        self.number = number


@api_view(['GET', 'POST', ])
def new_order(request):
    try:
        number = int(Orders.objects.latest('id').id)# + random.randrange(6) + request.user.id
    except Exception as e:
        number = random.randrange(10) + request.user.id
    order_number = Comment(number='RET#'+str(request.user.id)+str(''.join(random.choice('0123456789ABCDEF') for i in range(3)))+'-'+str(number))
    serializer = OrderNumberSerializer(order_number)
    return Response(serializer.data)


