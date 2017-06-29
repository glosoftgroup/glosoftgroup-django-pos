from django.utils.translation import pgettext_lazy


class OrderStatus:
    NEW = 'new'
    CANCELLED = 'cancelled'
    SHIPPED = 'shipped'
    PAYMENT_PENDING = 'payment-pending'
    FULLY_PAID = 'fully-paid'

    CHOICES = [
        (NEW, pgettext_lazy('order status', 'Processing')),
        (CANCELLED, pgettext_lazy('order status', 'Cancelled')),
        (SHIPPED, pgettext_lazy('order status', 'Shipped')),
        (PAYMENT_PENDING, pgettext_lazy('order status', 'Payment pending')),
        (FULLY_PAID, pgettext_lazy('order status', 'Fully paid'))]

class TransactionStatus:
    DEPOSIT = 'deposit'
    WITHDRAW = 'withdraw'   

    CHOICES = [
        (DEPOSIT, pgettext_lazy('drawer cash status', 'deposit')),
        (WITHDRAW, pgettext_lazy('drawer cash status', 'withdraw')),
       ]
