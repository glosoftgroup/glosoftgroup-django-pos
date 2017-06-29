from django.utils.translation import pgettext_lazy


class OrderStatus:
    PENDING = 'pending'
    CANCELLED = 'cancelled'
    SENT = 'shipped'
    PAYMENT_PENDING = 'payment-pending'
    FULLY_PAID = 'fully-paid'

    CHOICES = [
        (PENDING, pgettext_lazy('purchase order status', 'Processing')),
        (CANCELLED, pgettext_lazy('purchase order status', 'Cancelled')),
        (SENT, pgettext_lazy('purchase order status', 'sent')),
        (PAYMENT_PENDING, pgettext_lazy('purchase order status', 'Payment pending')),
        (FULLY_PAID, pgettext_lazy('purchase order status', 'Fully paid'))]
