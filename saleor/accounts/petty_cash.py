from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist
import datetime
from datetime import timedelta
from django.utils.dateformat import DateFormat
from decimal import Decimal
from ..dashboard.views import staff_member_required
from ..decorators import user_trail
from .models import PettyCash, Expenses

from structlog import get_logger

logger = get_logger(__name__)


def view(request):
    try:
        try:
            lastEntry = PettyCash.objects.latest('id')
            pd = DateFormat(lastEntry.created).format('Y-m-d')
            td = DateFormat(datetime.datetime.today()).format('Y-m-d')
            if td == pd:
                date = lastEntry.created
                amount = lastEntry.closing
                opening = lastEntry.opening
                added = lastEntry.added
                closing = lastEntry.closing
                expenses = Expenses.objects.filter(added_on__icontains=td).aggregate(Sum('amount'))['amount__sum']

                print expenses
            else:
                new_opening = lastEntry.closing
                new_balance = lastEntry.closing
                added = 0
                new_petty_cash = PettyCash(opening=new_opening, added=added, closing=new_balance)
                try:
                    expenses = Expenses.objects.filter(added_on__icontains=td).aggregate(Sum('amount'))['amount__sum']
                except:
                    expenses = 0
                new_petty_cash.save()

                date = new_petty_cash.created
                amount = new_petty_cash.closing
                opening = new_petty_cash.opening
                closing = new_petty_cash.closing
                added = new_petty_cash.added

        except:
            date = datetime.date.today()
            amount = 0
            opening = 0
            added = 0
            closing = 0
            expenses = 0

        data = {
            'pdate': date,
            'opening_amount': opening,
            'added_amount': added,
            'closing_amount': closing,
            'amount': amount,
            'expenses': expenses
        }

        return TemplateResponse(request, 'dashboard/accounts/petty_cash/view.html', data)
    except Exception, e:
        return HttpResponse(e)


@staff_member_required
def add(request):
    amount = Decimal(request.POST.get('amount'))

    try:
        try:
            lastEntry = PettyCash.objects.latest('id')
            pd = DateFormat(lastEntry.created).format('Y-m-d')
            td = DateFormat(datetime.datetime.today()).format('Y-m-d')
            if td == pd:
                lastEntry.added = lastEntry.added + amount
                lastEntry.closing = lastEntry.closing + amount
                lastEntry.save()
                balance = lastEntry.closing
            else:
                new_opening = lastEntry.closing
                new_balance = lastEntry.closing + amount
                new_petty_cash = PettyCash(opening=new_opening, added=amount, closing=new_balance)
                new_petty_cash.save()
                balance = new_petty_cash.closing
            user_trail(request.user.name, 'added KShs. ' + str(amount) + ' to petty cash balance of KShs. ' +
                       str(lastEntry.closing) + ' current balance is KShs. ' + str(lastEntry.closing + amount),
                       'update')
            logger.info(
                'User: ' + str(request.user.name) + 'added KShs. ' + str(amount) + ' to petty cash balance of KShs. ' +
                str(lastEntry.closing) + ' current balance is ' + str(lastEntry.closing + amount), 'update')
            return HttpResponse(balance)
        except:
            new_petty_cash = PettyCash(opening=amount, added=0, closing=amount)
            new_petty_cash.save()
            balance = new_petty_cash.closing
            user_trail(request.user.name,
                       'added KShs. ' + str(amount) + ' to petty cash, current balance is KShs. ' + str(balance),
                       'update')

            logger.info(
                'User: ' + str(request.user.name) + 'added KShs. ' + str(
                    amount) + ' to petty cash, current balance is ' + str(balance), 'update')
            return HttpResponse(balance)

    except Exception, e:
        logger.error(e)
        HttpResponse(e)


def balance(request):
    try:
        lastEntryId = PettyCash.objects.latest('id')
        amount = lastEntryId.closing
        return HttpResponse(amount)
    except Exception, e:
        amount = 0
        return HttpResponse(amount)


def expenditure(request):
    date = request.GET.get('date')
    try:
        if date:
            date = date
        else:
            date = DateFormat(datetime.datetime.today()).format('Y-m-d')

        pettyCash = dateFactorial(date)
        lastEntry = pettyCash.latest('id')

        pd = DateFormat(lastEntry.created).format('Y-m-d')
        td = DateFormat(datetime.datetime.today()).format('Y-m-d')
        if td == pd:
            dateToday = 1
            expenses = Expenses.objects.filter(added_on__icontains=pd).aggregate(Sum('amount'))['amount__sum']
            expenses = expenses
            added = lastEntry.added
            opening = lastEntry.opening
        else:
            dateToday = 0
            try:
                expenses = Expenses.objects.filter(added_on__icontains=date).aggregate(Sum('amount'))['amount__sum']
                if expenses:
                    expenses = expenses
                    added = lastEntry.added
                    opening = lastEntry.opening
                else:
                    expenses = 0
                    added = 0
                    opening = lastEntry.closing
            except:
                expenses = 0

        date = DateFormat(datetime.datetime.strptime(date, '%Y-%m-%d')).format('jS F Y')
        amount = lastEntry.closing
        opening = opening
        added = added
        closing = lastEntry.closing
        data = {
            'pdate': date,
            'opening_amount': opening,
            'added_amount': added,
            'closing_amount': closing,
            'amount': amount,
            'dateToday': dateToday,
            'expenses': expenses
        }
        return TemplateResponse(request, 'dashboard/accounts/petty_cash/expenditure.html', data)
    except BaseException, e:
        print (e)
        return TemplateResponse(request, 'dashboard/accounts/petty_cash/expenditure.html', {})


def dateFactorial(date):
    date = str(date)
    enteredDate = DateFormat(datetime.datetime.strptime(date, '%Y-%m-%d')).format('Y-m-d')
    firstDateEntry = DateFormat(PettyCash.objects.all().first().created).format('Y-m-d')
    if enteredDate < firstDateEntry:
        raise BaseException
    elif enteredDate == firstDateEntry:
        return PettyCash.objects.filter(created__icontains=firstDateEntry)
    else:
        try:
            query = PettyCash.objects.filter(created__icontains=enteredDate)
            if query.exists():
                return query
            else:
                raise ObjectDoesNotExist
        except ObjectDoesNotExist:
            return dateFactorial(
                DateFormat(datetime.datetime.strptime(date, '%Y-%m-%d') - timedelta(days=1)).format('Y-m-d'))
