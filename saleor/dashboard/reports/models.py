from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import HStoreField
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, RegexValidator
from django.db.models import F, Max, Q
from django.contrib.auth.models import Group


