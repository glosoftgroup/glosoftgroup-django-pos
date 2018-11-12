from ...credit.models import Credit
from ...sale.models import PaymentOption
from structlog import get_logger

logger = get_logger(__name__)


def clear_old_debts_using_change(change, instance):

    if change > 0:

        credit = Credit.objects.filter(
            status='payment-pending',
            customer_name=instance.customer_name).last()

        """ check if the instance argument object is truely an instance of credit.
            if it is, then exclude that id itself to avoid updating itself more than once if
            it's the last one.
        """
        if isinstance(instance, Credit):
            credit = Credit.objects.filter(
                status='payment-pending',
                customer_name=instance.customer_name).exclude(id=instance.id).last()

        if credit:

            debt_balance = credit.debt - change

            if debt_balance < 0:
                """ debt has been cleared """
                credit.amount_paid = credit.amount_paid + credit.debt
                credit.debt = 0
            else:
                """ debt remains """
                credit.debt = debt_balance
                credit.amount_paid = credit.amount_paid + change

            credit.payment_data = instance.payment_data[-1:]  # get the last payment option

            if credit.amount_paid >= credit.total_net:
                credit.status = 'fully-paid'
                credit.amount_paid = credit.total_net
                credit.debt = 0

                try:
                    option = credit.payment_data
                    pay_opt = PaymentOption.objects.get(pk=int(option['payment_id']))
                    credit.payment_options.add(pay_opt)
                except Exception as e:
                    logger.error("error adding the Payment Option " + str(e))

            credit.save()

            logger.info(
                "credit of id: " + str(credit.pk) + ", balance: " + str(credit.debt) + ", status: " + str(
                    credit.status))

            if debt_balance < 0:
                """ debt balance < 0 when the change amount has a balance
                    hence convert the negative to positive for an actual balance
                    and then call clear_old_debts_using_change(change_balance, instance) again
                """
                debt_balance = debt_balance * -1
                clear_old_debts_using_change(debt_balance, instance)
