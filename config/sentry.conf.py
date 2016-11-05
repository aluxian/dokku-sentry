# This file is just Python, with a touch of Django which means
# you can inherit and tweak settings to your heart's content.

from sentry.conf.server import *  # NOQA
from sentry.utils.types import Bool

import os
import os.path

CONF_ROOT = os.path.dirname(__file__)

# Sentry settings
SENTRY_FEATURES['auth:register'] = False

# Get and parse dokku env vars
db_url = os.environ['DATABASE_URL']
redis_url = os.environ['REDIS_URL']
db_url_parts = urlparse.urlparse(db_url)
redis_url_parts = urlparse.urlparse(redis_url)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': db_url_parts.path[1:],
        'USER': db_url_parts.username,
        'PASSWORD': db_url_parts.password,
        'HOST': db_url_parts.hostname,
        'PORT': db_url_parts.port,
    }
}

# You should not change this setting after your database has been created
# unless you have altered all schemas first
SENTRY_USE_BIG_INTS = True

# If you're expecting any kind of real traffic on Sentry, we highly recommend
# configuring the CACHES and Redis settings

###########
# General #
###########

# Instruct Sentry that this install intends to be run by a single organization
# and thus various UI optimizations should be enabled.
SENTRY_SINGLE_ORGANIZATION = True

#########
# Redis #
#########

# Generic Redis configuration used as defaults for various things including:
# Buffers, Quotas, TSDB

SENTRY_OPTIONS.update({
    'redis.clusters': {
        'default': {
            'hosts': {
                0: {
                    'host': redis_url_parts.hostname,
                    'port': redis_url_parts.port,
                    'password': redis_url_parts.password,
                },
            },
        },
    },
})

#########
# Cache #
#########

# Sentry currently utilizes two separate mechanisms. While CACHES is not a
# requirement, it will optimize several high throughput patterns.

# If you wish to use memcached, install the dependencies and adjust the config
# as shown:
#
#   pip install python-memcached
#
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': ['127.0.0.1:11211'],
#     }
# }

# A primary cache is required for things such as processing events
SENTRY_CACHE = 'sentry.cache.redis.RedisCache'

#########
# Queue #
#########

# See https://docs.getsentry.com/on-premise/server/queue/ for more
# information on configuring your queue broker and workers. Sentry relies
# on a Python framework called Celery to manage queues.

BROKER_URL = redis_url

###############
# Rate Limits #
###############

# Rate limits apply to notification handlers and are enforced per-project
# automatically.

SENTRY_RATELIMITER = 'sentry.ratelimits.redis.RedisRateLimiter'

##################
# Update Buffers #
##################

# Buffers (combined with queueing) act as an intermediate layer between the
# database and the storage API. They will greatly improve efficiency on large
# numbers of the same events being sent to the API in a short amount of time.
# (read: if you send any kind of real data to Sentry, you should enable buffers)

SENTRY_BUFFER = 'sentry.buffer.redis.RedisBuffer'

##########
# Quotas #
##########

# Quotas allow you to rate limit individual projects or the Sentry install as
# a whole.

SENTRY_QUOTAS = 'sentry.quotas.redis.RedisQuota'

########
# TSDB #
########

# The TSDB is used for building charts as well as making things like per-rate
# alerts possible.

SENTRY_TSDB = 'sentry.tsdb.redis.RedisTSDB'

###########
# Digests #
###########

# The digest backend powers notification summaries.

SENTRY_DIGESTS = 'sentry.digests.backends.redis.RedisBackend'

################
# File storage #
################

# Any Django storage backend is compatible with Sentry. For more solutions see
# the django-storages package: https://django-storages.readthedocs.org/en/latest/

SENTRY_FILESTORE = 'django.core.files.storage.FileSystemStorage'
SENTRY_FILESTORE_OPTIONS = {'location': '/tmp/sentry-files'}

##############
# Web Server #
##############

SENTRY_WEB_HOST = '0.0.0.0'
SENTRY_WEB_PORT = os.environ.get('PORT')

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

###############
# Mail Server #
###############

email = os.environ.get('SENTRY_EMAIL_HOST')
if email:
    SENTRY_OPTIONS['mail.backend'] = 'smtp'
    SENTRY_OPTIONS['mail.host'] = email
    SENTRY_OPTIONS['mail.password'] = os.environ.get('SENTRY_EMAIL_PASSWORD') or ''
    SENTRY_OPTIONS['mail.username'] = os.environ.get('SENTRY_EMAIL_USER') or ''
    SENTRY_OPTIONS['mail.port'] = int(os.environ.get('SENTRY_EMAIL_PORT') or 25)
    SENTRY_OPTIONS['mail.use-tls'] = Bool(os.environ.get('SENTRY_EMAIL_USE_TLS', False))
else:
    SENTRY_OPTIONS['mail.backend'] = 'dummy'
    SENTRY_OPTIONS['mail.host'] = 'localhost'
    SENTRY_OPTIONS['mail.password'] = ''
    SENTRY_OPTIONS['mail.username'] = ''
    SENTRY_OPTIONS['mail.port'] = 25
    SENTRY_OPTIONS['mail.use-tls'] = False

# The email address to send on behalf of
SENTRY_OPTIONS['mail.from'] = os.environ.get('SENTRY_SERVER_EMAIL') or 'root@localhost'

# If you're using mailgun for inbound mail, set your API key and configure a
# route to forward to /api/hooks/mailgun/inbound/
MAILGUN_API_KEY = os.environ.get('SENTRY_MAILGUN_API_KEY') or ''

# If you specify a MAILGUN_API_KEY, you definitely want EMAIL_REPLIES
if MAILGUN_API_KEY:
    SENTRY_ENABLE_EMAIL_REPLIES = True
else:
    SENTRY_ENABLE_EMAIL_REPLIES = Bool(os.environ.get('SENTRY_ENABLE_EMAIL_REPLIES', False))

if SENTRY_ENABLE_EMAIL_REPLIES:
    SENTRY_SMTP_HOSTNAME = os.environ.get('SENTRY_SMTP_HOSTNAME') or 'localhost'
