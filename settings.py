# Django settings for stats project.

from django_auth_ldap.config import LDAPSearch, PosixGroupType
import ldap
import logging
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

ALLOWED_HOSTS = ['*',] 

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
        },
        'surveys': {    
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'surveys',
            'USER': 'www',
            'PASSWORD': 'TODO: enter-password',            
        },
    })

# Database routers
DATABASE_ROUTERS = ['routers.DBRouter']

# Date that we started collecting data [Y, M, D]
REPORTS_START_DATE = datetime.datetime(2013, 9, 01) 

HOUDINI_REPORTS_START_DATE = datetime.datetime(2014, 4, 13) 

                                  
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
    
if sys.platform.startswith('linux'):
    GEOIP_PATH = "/usr/share/GeoIP/GeoIP.dat"
else:
    GEOIP_PATH = "./"    


AUTH_LDAP_SERVER_URI = "ldap://internal.sidefx.com"

AUTH_LDAP_BIND_DN = "cn=licenseadmin,dc=sidefx,dc=com"
AUTH_LDAP_BIND_PASSWORD = "test"
AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=people,dc=sidefx,dc=com",\
                                   ldap.SCOPE_SUBTREE, "(uid=%(user)s)") 

AUTH_LDAP_FIND_GROUP_PERMS = True 
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 300
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
AUTH_LDAP_MIRROR_GROUPS = True
AUTH_LDAP_ALWAYS_UPDATE_USER = True

# Populate the Django user from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = {
     "first_name": "givenName",
     "last_name": "sn",
     "email": "mail"
}

AUTH_LDAP_PROFILE_ATTR_MAP = {
    "home_directory": "homeDirectory"}

AUTH_LDAP_PROFILE_ATTR_MAP = {
    "gid_Number": "gidNumber"
}

# enables a Django project to authenticate against any LDAP server
AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_LDAP_USER_FLAGS_BY_GROUP = {   
    "is_staff": "cn=staff,ou=groups,dc=sidefx,dc=com",
    "is_superuser": "cn=admin,ou=groups,dc=sidefx,dc=com",
    "is_license": "cn=license,ou=groups,dc=sidefx,dc=com",
    "is_support": "cn=support,ou=groups,dc=sidefx,dc=com",
    "is_r&d": "cn=r&d,ou=groups,dc=sidefx,dc=com",
    "is_sales": "cn=sales,ou=groups,dc=sidefx,dc=com",
    "is_assetstore": "cn=assetstore,ou=groups,dc=sidefx,dc=com",
    "is_audio": "cn=audio,ou=groups,dc=sidefx,dc=com",
    "is_bizgroup": "cn=bizgroup,ou=groups,dc=sidefx,dc=com",
    "is_cdrom": "cn=cdrom,ou=groups,dc=sidefx,dc=com",
    "is_execs": "cn=execs,ou=groups,dc=sidefx,dc=com",
    "is_hooke": "cn=hooke,ou=groups,dc=sidefx,dc=com",
    "is_mware": "cn=mware,ou=groups,dc=sidefx,dc=com",
    "is_paulgroup": "cn=paulgroup,ou=groups,dc=sidefx,dc=com",
    "is_plugdev": "cn=plugdev,ou=groups,dc=sidefx,dc=com",
    "is_projects": "cn=projects,ou=groups,dc=sidefx,dc=com",
    "is_smadmin": "cn=smadmin,ou=groups,dc=sidefx,dc=com",
    "is_video": "cn=video,ou=groups,dc=sidefx,dc=com",
    "is_webcal_admin": "cn=webcal_admin,ou=groups,dc=sidefx,dc=com",
}

# Set up the basic group parameters.
# Note: THis must be set or raise ImproperlyConfigured("AUTH_LDAP_GROUP_TYPE 
# must be an LDAPGroupType instance.")
# AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=groups,dc=sidefx,dc=com",
#     ldap.SCOPE_SUBTREE, "(objectClass=groupOfNames)"
# )

# AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr="cn")


AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=groups,dc=sidefx,dc=com",
    ldap.SCOPE_SUBTREE, "(objectClass=posixGroup)"
)
AUTH_LDAP_GROUP_TYPE = PosixGroupType(name_attr='cn')

logger = logging.getLogger('django_auth_ldap')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

