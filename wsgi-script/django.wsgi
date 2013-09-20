import os
import sys

sys.path.append('/var/www')
sys.path.append('/var/www/stats')
os.environ['DJANGO_SETTINGS_MODULE'] = 'stats.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

