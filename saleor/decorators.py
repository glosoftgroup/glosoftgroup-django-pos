from django.http import HttpResponseForbidden
from .userprofile.models import UserTrail
from django.core.exceptions import ObjectDoesNotExist
from datetime import date
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

from structlog import get_logger

logger = get_logger(__name__)


def permission_decorator(argument):
    def permitted_users_only(function):
        def wrap(request, *args, **kwargs):
            if request.user.has_perm(argument):
                logger.info('status: 200, ' + str(argument) + ' permission granted for ' + str(request.user))
                return function(request, *args, **kwargs)
            else:
                logger.debug('status: 403, ' + str(argument) + ' permission denied for ' + str(request.user))
                raise PermissionDenied()

        return wrap

    return permitted_users_only


def user_trail(name, action, tag=None):
    record = UserTrail(name=name, action=action, crud=tag, date=date.today())
    record.save()


class EmailOrUsernameModelBackend(object):
    """
    This is a ModelBacked that allows authentication with either a username or an email address.

    """

    def authenticate(self, username=None, password=None):
        username = username.lower()
        if '@' in username:
            kwargs = {'email': username}
        else:
            kwargs = {'name': username}
        try:
            user = get_user_model().objects.get(**kwargs)
            if user.check_password(password):
                return user
        except ObjectDoesNotExist:
            return None

    def get_user(self, username):
        try:
            return get_user_model().objects.get(pk=username)
        except get_user_model().DoesNotExist:
            return None


def friendly_csrf_failure_view(request, reason="SuspiciousOperation", template_name="403_csrf.html"):
    return HttpResponseForbidden('Not Authorized. Please contact your Administrator.')
