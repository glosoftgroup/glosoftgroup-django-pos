from saleor.site.models import SiteSettings
import datetime


def is_business_time():
    """
    Check if it's business hours
    :return: True if business is open else false
    """
    settings = SiteSettings.objects.get(pk=1)
    closing_time = settings.closing_time
    opening_time = settings.opening_time
    # format = '%H:%M %p'
    now = datetime.datetime.time(datetime.datetime.now())

    if closing_time is None and opening_time is not None:
        if now < opening_time:
            return False
    if opening_time is None and closing_time is not None:
        if now > closing_time:
            return False
    if opening_time is not None and closing_time is not None:
        if now < opening_time:
            return False
        if now > closing_time:
            return False
        else:
            return True
