import os
import sys

sys.path.append('/home/yele/dev_external/django')
sys.path.append('/home/yele/dev_external/django/stats')
os.environ['DJANGO_SETTINGS_MODULE'] = 'stats.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

