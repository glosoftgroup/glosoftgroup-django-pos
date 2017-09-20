from __future__ import unicode_literals

import ast
import os
import os.path
import datetime
import dj_database_url
import dj_email_url
from django.contrib.messages import constants as messages
import django_cache_url
from django.utils.dateformat import DateFormat

dateToday = datetime.datetime.now()
thisDate = dateToday.strftime('%d-%m-%Y')
thisMonth = dateToday.strftime('%b')
dayName = dateToday.strftime("%a")

thisMonthDirectory = "C:\\Users\\Public\\PosServer\\logs\\"
info_path = thisMonthDirectory+'\\'+thisDate+'_info.log'
error_path = thisMonthDirectory+'\\'+thisDate+'_error.log'
debug_path = thisMonthDirectory+'\\'+thisDate+'_debug.log'
warning_path = thisMonthDirectory+'\\'+thisDate+'_warning.log'

if not os.path.exists(thisMonthDirectory):
    os.makedirs(thisMonthDirectory)

DEBUG = ast.literal_eval(os.environ.get('DEBUG', 'True'))

SITE_ID = 1

PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))

ROOT_URLCONF = 'saleor.urls'

WSGI_APPLICATION = 'saleor.wsgi.application'

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)
MANAGERS = ADMINS
INTERNAL_IPS = os.environ.get('INTERNAL_IPS', '127.0.0.1').split()

CACHES = {'default': django_cache_url.config()}

if os.environ.get('REDIS_URL'):
    CACHES['default'] = {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL')}

DATABASES = {
    'default': dj_database_url.config(
        default='postgres://saleor:saleor@localhost:5432/saleor',
        conn_max_age=600)}

TIME_ZONE = 'Africa/Nairobi'
LANGUAGE_CODE = 'en-us'
LOCALE_PATHS = [os.path.join(PROJECT_ROOT, 'locale')]
USE_I18N = True
USE_L10N = True
USE_TZ = True

EMAIL_URL = os.environ.get('EMAIL_URL')
SENDGRID_USERNAME = os.environ.get('SENDGRID_USERNAME')
SENDGRID_PASSWORD = os.environ.get('SENDGRID_PASSWORD')
if not EMAIL_URL and SENDGRID_USERNAME and SENDGRID_PASSWORD:
    EMAIL_URL = 'smtp://%s:%s@smtp.sendgrid.net:587/?tls=True' % (
        SENDGRID_USERNAME, SENDGRID_PASSWORD)
email_config = dj_email_url.parse(EMAIL_URL or 'console://')

EMAIL_FILE_PATH = email_config['EMAIL_FILE_PATH']
EMAIL_HOST_USER = email_config['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = email_config['EMAIL_HOST_PASSWORD']
EMAIL_HOST = email_config['EMAIL_HOST']
EMAIL_PORT = email_config['EMAIL_PORT']
EMAIL_BACKEND = email_config['EMAIL_BACKEND']
EMAIL_USE_TLS = email_config['EMAIL_USE_TLS']
EMAIL_USE_SSL = email_config['EMAIL_USE_SSL']

# EMAIL_HOST_USER = 'alexkiburu@gmail.com'
# EMAIL_HOST_PASSWORD = 'unicorn-tech'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# DEFAULT_FROM_EMAIL = 'alexkiburu@gmail.com'

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')
ORDER_FROM_EMAIL = os.getenv('ORDER_FROM_EMAIL', DEFAULT_FROM_EMAIL)

CUSTOMER_CODE = os.environ.get('CUSTOMER_CODE')

MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    ('assets', os.path.join(PROJECT_ROOT, 'saleor', 'static', 'assets')),
    ('images', os.path.join(PROJECT_ROOT, 'saleor', 'static', 'images')),
    ('backend', os.path.join(PROJECT_ROOT, 'saleor', 'static', 'backend')),
    ('dashboard', os.path.join(PROJECT_ROOT, 'saleor', 'static', 'dashboard'))
]
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
]

context_processors = [
    'django.contrib.auth.context_processors.auth',
    'django.template.context_processors.debug',
    'django.template.context_processors.i18n',
    'django.template.context_processors.media',
    'django.template.context_processors.static',
    'django.template.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.template.context_processors.request',
    'saleor.core.context_processors.default_currency',
    'saleor.core.context_processors.categories',
    'saleor.cart.context_processors.cart_counter',
    'saleor.core.context_processors.search_enabled',
    'saleor.site.context_processors.settings',
    'saleor.core.context_processors.webpage_schema',
    'social_django.context_processors.backends',
    'social_django.context_processors.login_redirect',
]

loaders = [
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # TODO: this one is slow, but for now need for mptt?
    'django.template.loaders.eggs.Loader']

if not DEBUG:
    loaders = [('django.template.loaders.cached.Loader', loaders)]

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(PROJECT_ROOT, 'templates')],
    'OPTIONS': {
        'debug': DEBUG,
        'context_processors': context_processors,
        'loaders': loaders,
        'string_if_invalid': '<< MISSING VARIABLE "%s" >>' if DEBUG else ''}}]

# Make this unique, and don't share it with anybody.
# SECRET_KEY = os.environ.get('SECRET_KEY')
SECRET_KEY = 'dc62qi9pc0h=8a(mggch-%qr*ya5l4wrpapal7t(=sa=gs4@j8'

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'babeldjango.middleware.LocaleMiddleware',
    'saleor.core.middleware.DiscountMiddleware',
    'saleor.core.middleware.GoogleAnalytics',
    'saleor.core.middleware.CountryMiddleware',
    'saleor.core.middleware.CurrencyMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'saleor.core.middleware.SettingsMiddleware',
]

INSTALLED_APPS = [
    # External apps that need to go before django's
    'storages',

    # Django modules
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'django.contrib.postgres',
    'django.contrib.humanize',

    # Local apps
    'saleor.accounts',
    'saleor.userprofile',
    'saleor.discount',
    'saleor.product',    
    'saleor.cart',
    'saleor.checkout',
    'saleor.core',
    'saleor.graphql',
    'saleor.order',
    'saleor.dashboard',
    'saleor.shipping',
    'saleor.search',
    'saleor.site',
    'saleor.data_feeds',
    'saleor.sale',
    'saleor.api',
    'saleor.customer',
    'saleor.supplier',
    'saleor.payment',
    'saleor.purchase',
    'saleor.smessages',
    'saleor.invoice',
    'saleor.credit',

    # External apps
    'versatileimagefield',
    'babeldjango',
    'bootstrap3',
    'django_prices',
    'django_prices_openexchangerates',
    'emailit',
    'graphene_django',
    'mptt',
    'payments',
    'materializecssform',
    'rest_framework',
    'webpack_loader',
    'social_django',
    'django_countries',
    'rest_framework.authtoken',
    'notifications',
    # 'chartjs',
]

U_LOGFILE_SIZE = 5 * 1024 * 1024
U_LOGFILE_COUNT = 10
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'standard': {
            'format': '[%(asctime)s] %(levelname)s %(name)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '[%(asctime)s] %(levelname)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'handlers': {
        'null': {
                'class': 'logging.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_true'],
            'formatter': 'simple'
        },
        'debug_logfile': {
            'level': 'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename':debug_path,
            'maxBytes': U_LOGFILE_SIZE,
            'backupCount': U_LOGFILE_COUNT,
            'formatter': 'standard'
        },
        'error_logfile': {
            'level': 'ERROR',
            'class':'logging.handlers.RotatingFileHandler',
            'filename':error_path,
            'maxBytes': U_LOGFILE_SIZE,
            'backupCount': U_LOGFILE_COUNT,
            'formatter': 'standard'
        },
        'warning_logfile': {
            'level': 'WARNING',
            'class':'logging.handlers.RotatingFileHandler',
            'filename':warning_path,
            'maxBytes': U_LOGFILE_SIZE,
            'backupCount': U_LOGFILE_COUNT,
            'formatter': 'standard'
        },
        'info_logfile': {
            'level': 'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'filename':info_path,
            'maxBytes': U_LOGFILE_SIZE,
            'backupCount': U_LOGFILE_COUNT,
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django.security.*': {
                'handlers': ['error_logfile','null'],
                'level': 'ERROR',
                'propagate': True
        },
        'django.security.csrf': {
                'handlers': ['warning_logfile'],
                'level': 'WARNING',
                'propagate': True
        },
        'django.request': {
            'handlers': ['warning_logfile'], #['error_logfile'], #['mail_admins'],
            # 'level': 'WARNING', #''ERROR',
            'propagate': True
        },
        'saleor': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True
        },
        'debug_logger': {
            'handlers': ['debug_logfile'],
            'level': 'DEBUG',
            'propagate': True
        },
        'error_logger': {
            'handlers': ['error_logfile'],
            'level': 'DEBUG',
            'propagate': True
        },
        'info_logger': {
            'handlers': ['info_logfile'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}

CSRF_FAILURE_VIEW = 'saleor.decorators.friendly_csrf_failure_view'
AUTH_USER_MODEL = 'userprofile.User'

LOGIN_URL = '/'

DEFAULT_COUNTRY = 'KE'
DEFAULT_CURRENCY = 'KES'
AVAILABLE_CURRENCIES = [DEFAULT_CURRENCY]

OPENEXCHANGERATES_API_KEY = os.environ.get('OPENEXCHANGERATES_API_KEY')

ACCOUNT_ACTIVATION_DAYS = 3

# loyalty point equivalence value default KES 100 = 1point
LOYALTY_POINT_EQUIVALENCE = 100
LOGIN_REDIRECT_URL = 'home'

GOOGLE_ANALYTICS_TRACKING_ID = os.environ.get('GOOGLE_ANALYTICS_TRACKING_ID')


def get_host():
    from saleor.site.utils import get_domain
    return get_domain()

PAYMENT_HOST = get_host

PAYMENT_MODEL = 'order.Payment'

PAYMENT_VARIANTS = {
    'default': ('payments.dummy.DummyProvider', {})}

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

CHECKOUT_PAYMENT_CHOICES = [
    ('default', 'Dummy provider')]

MESSAGE_TAGS = {
    messages.ERROR: 'danger'}

LOW_STOCK_THRESHOLD = 10
MAX_CART_LINE_QUANTITY = os.environ.get('MAX_CART_LINE_QUANTITY', 50)

PAGINATE_BY = 16

BOOTSTRAP3 = {
    'set_placeholder': False,
    'set_required': False,
    'success_css_class': 'success',
    'form_renderers': {
        'default': 'saleor.core.utils.form_renderer.FormRenderer',
    },
}

TEST_RUNNER = ''
ALLOWED_HOSTS = ['*']

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Amazon S3 configuration
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_MEDIA_BUCKET_NAME = os.environ.get('AWS_MEDIA_BUCKET_NAME')
AWS_QUERYSTRING_AUTH = ast.literal_eval(
    os.environ.get('AWS_QUERYSTRING_AUTH', 'False'))

if AWS_STORAGE_BUCKET_NAME:
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

if AWS_MEDIA_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = 'saleor.core.storages.S3MediaStorage'
    THUMBNAIL_DEFAULT_STORAGE = DEFAULT_FILE_STORAGE

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

VERSATILEIMAGEFIELD_RENDITION_KEY_SETS = {
    'defaults': [
        ('product_gallery', 'crop__540x540'),
        ('product_gallery_2x', 'crop__1080x1080'),
        ('product_small', 'crop__60x60'),
        ('product_small_2x', 'crop__120x120'),
        ('product_list', 'crop__255x255'),
        ('product_list_2x', 'crop__510x510')]}

VERSATILEIMAGEFIELD_SETTINGS = {
    # Images should be pre-generated on Production environment
    'create_images_on_demand': ast.literal_eval(
        os.environ.get('CREATE_IMAGES_ON_DEMAND', 'True')),
}

PLACEHOLDER_IMAGES = {
    60: 'images/placeholder60x60.png',
    120: 'images/placeholder120x120.png',
    255: 'images/placeholder255x255.png',
    540: 'images/placeholder540x540.png',
    1080: 'images/placeholder1080x1080.png'
}

DEFAULT_PLACEHOLDER = 'images/placeholder255x255.png'

WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': 'assets/',
        'STATS_FILE': os.path.join(PROJECT_ROOT, 'webpack-bundle.json'),
        'POLL_INTERVAL': 0.1,
        'IGNORE': [
            r'.+\.hot-update\.js',
            r'.+\.map']}}


LOGOUT_ON_PASSWORD_CHANGE = False


ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
SEARCHBOX_URL = os.environ.get('SEARCHBOX_URL')
BONSAI_URL = os.environ.get('BONSAI_URL')
# We'll support couple of elasticsearch add-ons, but finally we'll use single
# variable
ES_URL = ELASTICSEARCH_URL or SEARCHBOX_URL or BONSAI_URL or ''
if ES_URL:
    SEARCH_BACKENDS = {
        'default': {
            'BACKEND': 'saleor.search.backends.elasticsearch2',
            'URLS': [ES_URL],
            'INDEX': os.environ.get('ELASTICSEARCH_INDEX_NAME', 'storefront'),
            'TIMEOUT': 5,
            'AUTO_UPDATE': True},
        'dashboard': {
            'BACKEND': 'saleor.search.backends.dashboard',
            'URLS': [ES_URL],
            'INDEX': os.environ.get('ELASTICSEARCH_INDEX_NAME', 'storefront'),
            'TIMEOUT': 5,
            'AUTO_UPDATE': False}
    }
else:
    SEARCH_BACKENDS = {}


GRAPHENE = {
    'MIDDLEWARE': [
        'graphene_django.debug.DjangoDebugMiddleware'
    ],
    'SCHEMA': 'saleor.graphql.api.schema',
    'SCHEMA_OUTPUT': os.path.join(
        PROJECT_ROOT, 'saleor', 'static', 'schema.json')
}

SITE_SETTINGS_ID = 1

AUTHENTICATION_BACKENDS = [
    'saleor.registration.backends.facebook.CustomFacebookOAuth2',
    'saleor.registration.backends.google.CustomGoogleOAuth2',
    'saleor.decorators.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

SOCIAL_AUTH_PIPELINE = [
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
]

SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True
SOCIAL_AUTH_USER_MODEL = AUTH_USER_MODEL
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id, email'}

# REST_FRAMEWORK = {
# 	# Use Django's standard `django.contrib.auth` permissions,
# 	# or allow read-only access for unauthenticated users.
# 	'DEFAULT_PERMISSION_CLASSES': [
# 		'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
# 	]
# }

'''
    rest framework configuration
'''
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'saleor.jwt_payload.custom_exception_handler',
    'DEFAULT_RENDERER_CLASSES':(
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )

}

'''
    JWT REST FRAMEWORK CONFUGURATIONS
'''
from datetime import timedelta

JWT_AUTH = {
    'JWT_ENCODE_HANDLER':
    'rest_framework_jwt.utils.jwt_encode_handler',

    'JWT_DECODE_HANDLER':
    'rest_framework_jwt.utils.jwt_decode_handler',

    'JWT_PAYLOAD_HANDLER':
    'rest_framework_jwt.utils.jwt_payload_handler',

    'JWT_PAYLOAD_GET_USER_ID_HANDLER':
    'rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler',

    'JWT_RESPONSE_PAYLOAD_HANDLER':
    'saleor.jwt_payload.jwt_response_payload_handler',
    'JWT_EXPIRATION_DELTA':
     timedelta(days=2),

}

TIME_INPUT_FORMATS = ['%H:%M %p']

# notifications
NOTIFICATION_TEST = 1
NOTIFICATIONS_SOFT_DELETE = True

# smessages
MESSAGES_SOFT_DELETE = True
