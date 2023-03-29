import os
import sys
import django.conf
from django.core.wsgi import get_wsgi_application

sys.path.append('/var/www')
sys.path.append('/var/www/stats')
sys.path.append('/var/www/stats/stats_core')

# See http://stackoverflow.com/questions/11383176/problems-hosting-multiple-django-sites-settings-cross-over
django.conf.ENVIRONMENT_VARIABLE = "DJANGO_STATS_SETTINGS_MODULE"
os.environ['DJANGO_STATS_SETTINGS_MODULE'] = 'stats_core.settings'

application = get_wsgi_application()
