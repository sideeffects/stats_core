# Django settings for stats project.

import os
import sys
import datetime
import socket

# Make sure this folder is the first one in the search path so we pick up
# our googlecharts instead of the system's.
_this_dir = os.path.normpath(os.path.dirname(__file__))
if sys.path[0] != _this_dir:
    sys.path.insert(0, _this_dir)

PRODUCTION_LOGGING_SERVER_NAME = "florida"
PRODUCTION_QUERY_SERVER_NAME = "yuma"

IS_PRODUCTION_LOGGING_SERVER = (
    socket.gethostname() == PRODUCTION_LOGGING_SERVER_NAME)
IS_PRODUCTION_QUERY_SERVER = (
    socket.gethostname() == PRODUCTION_QUERY_SERVER_NAME)
IS_PRODUCTION_SERVER = (
    IS_PRODUCTION_LOGGING_SERVER or IS_PRODUCTION_QUERY_SERVER)

# If it's not a production server, then the server is both the logging and
# query server.
IS_LOGGING_SERVER = not IS_PRODUCTION_SERVER or IS_PRODUCTION_LOGGING_SERVER
IS_QUERY_SERVER = not IS_PRODUCTION_SERVER or IS_PRODUCTION_QUERY_SERVER

DEBUG = True #not IS_PRODUCTION_SERVER
TEMPLATE_DEBUG = DEBUG
SHOW_DEBUG_TOOLBAR = not IS_PRODUCTION_SERVER

ADMIN_USER = 'admin'
ADMINS = (
    ('stats dev1', 'yele@sidefx.com'),
    ('stats dev2', 'luke@sidefx.com'),
)
MANAGERS = ADMINS

_this_dir = os.path.normpath(os.path.dirname(__file__))
_base_dir = os.path.abspath(os.path.join(_this_dir, os.pardir))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        #'NAME': 'stats',
        'NAME': 'stats_django_skeleton',
        'USER': 'www',
        'PASSWORD': 'TODO: enter-password',
    },
    'stats': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'stats',
        'USER': 'www',
        'PASSWORD': 'TODO: enter-password',
        'HOST': (PRODUCTION_LOGGING_SERVER_NAME
            if IS_PRODUCTION_QUERY_SERVER else '')
    },
}

if IS_QUERY_SERVER:
    DATABASES.update({
        'licensedb': {    
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'licensedb',
            'USER': 'www',
            'PASSWORD': 'TODO: enter-password',
            'HOST': (''
                if IS_PRODUCTION_QUERY_SERVER else 'sandbox.sidefx.com'),
        },
        'mambo': {    
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'mambo',
            'USER': 'www',
            'PASSWORD': 'TODO: enter-password',
            'HOST': (PRODUCTION_LOGGING_SERVER_NAME
                if IS_PRODUCTION_QUERY_SERVER else ''),
        },
        'surveys': {    
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'surveys',
            'USER': 'www',
            'PASSWORD': 'TODO: enter-password',
            'HOST': (PRODUCTION_LOGGING_SERVER_NAME
                if IS_PRODUCTION_QUERY_SERVER else ''),
        },
    })

# Database routers
DATABASE_ROUTERS = ['routers.DBRouter']

# Date that we started collecting data [Y, M, D]
REPORTS_START_DATE = datetime.datetime(2013, 9, 01) 
                                  
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = ('/stats/static/' if IS_PRODUCTION_SERVER else '/static/')

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

# Location where we store the admin static files
ADMIN_ROOT = os.path.join(_this_dir, "static/admin")

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '_m3=p2y3#1cv%@!cy$(iarr##!9aixne_@7(hm)!9yl#=2jy2h'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

if SHOW_DEBUG_TOOLBAR:
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',)
    
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

INTERNAL_IPS = ('127.0.0.1',)    
ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
     os.path.join(_this_dir, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    #'django.contrib.auth.context_processors.csrf',
        
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'googlecharts',
    'south',
    'houdini_stats',
)

if SHOW_DEBUG_TOOLBAR:
    INSTALLED_APPS += (
        'debug_toolbar',
    )

if IS_QUERY_SERVER:
    INSTALLED_APPS += (
        'houdini_licenses',
        'houdini_forum',
        'houdini_surveys',
        
    )

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
#    'filters': {
#     'require_debug_false': {
#         '()': 'django.utils.log.RequireDebugFalse'
#     }
#     },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
#            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Page to use for logins.
if len(sys.argv) >= 2 and sys.argv[1] == 'runserver':
    LOGIN_URL = '/login'
    LOGIN_REDIRECT_URL = '/'
else:
    LOGIN_URL = '/stats/login'
    LOGIN_REDIRECT_URL = '/stats'

