# Django settings for stats project.
import django

import os
import sys
import datetime
import socket

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

_django_version = [int(x) for x in django.get_version().split(".")[:2]]

# Make sure this folder is the first one in the search path so we pick up
# our googlecharts instead of the system's.
_this_dir = os.path.normpath(os.path.dirname(__file__))
if sys.path[0] != _this_dir:
    sys.path.insert(0, _this_dir)

_base_dir = os.path.abspath(os.path.join(_this_dir, os.pardir))

# Silence warnings about replacing a foreign key that is a primary key with
# a one to one field.
SILENCED_SYSTEM_CHECKS = ["fields.W342"]

# Stats applications and reports modules to include. 
# Each included app will extend this list 
STATS_APPLICATIONS = ()
REPORT_MODULES = ()
TOP_MENU_OPTIONS = OrderedDict()

DEBUG = True
TEMPLATE_DEBUG = DEBUG
SHOW_DEBUG_TOOLBAR = False

ALLOWED_HOSTS = ['*',] 

ADMIN_USER = 'admin'
ADMINS = ()
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'stats_django_skeleton',
        'USER': 'www-stats',
        'PASSWORD': 'TODO: enter-password',
    },
    'stats': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'stats',
        'USER': 'www-stats',
        'PASSWORD': 'TODO: enter-password',
    },
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = '<TODO: generate your own secret key!>'

# Database routers
DATABASE_ROUTERS = ['routers.DBRouter']

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Date that we started collecting data [Y, M, D]
REPORTS_START_DATE = datetime.datetime(2013, 9, 01) 

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Toronto'

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
STATIC_URL = '/stats/static/'

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
    'stats_main',
)

if _django_version[0] == 1 and _django_version[1] <= 6:
    INSTALLED_APPS += ("south",)

if SHOW_DEBUG_TOOLBAR:
    INSTALLED_APPS += (
        'debug_toolbar',
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
            'filters': [],
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
    
if sys.platform.startswith('linux'):
    GEOIP_PATH = "/usr/share/GeoIP/GeoIP.dat"
else:
    GEOIP_PATH = "./"    

#----------------------------------------------------------------------------

HOUDINI_REPORTS_START_DATE = datetime.datetime(2014, 4, 13) 

IS_QUERY_SERVER = True
IS_LOGGING_SERVER = True

# Extension apps to be added to stats_core 
STATS_EXTENSIONS = (
    # In the current version stats_core project ALWAYS needs
    # the stats_houdini extension                
    "../stats_houdini", 
)

# Import stats_core local_settings if one exists
try:
    from local_settings import *
except ImportError:
    pass

# Loop through the stats extensions, add them to the sys.path, load each of
# their local_settings, and give them a chance to append to STATS_APPLICATIONS.
for extension_relative_dir in STATS_EXTENSIONS:
    extension_dir = os.path.normpath(
        os.path.join(_this_dir, extension_relative_dir))
    sys.path.append(extension_dir)
   
    try:
        execfile(os.path.join(extension_dir, "local_settings.py"))
    except IOError:
        pass

# Now that we know all the STATS_APPLICATIONS, we can tell Django by updating
# INSTALLED_APPS.
INSTALLED_APPS += tuple(set(STATS_APPLICATIONS) - set(INSTALLED_APPS))

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
