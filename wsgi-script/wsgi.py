import os
import sys
sys.path.append('/var/www')
sys.path.append('/var/www/stats')
sys.path.append('/var/www/stats/stats_core')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stats_core.settings")

from django.core.wsgi import get_wsgi_application


os.environ['DJANGO_STATS_SETTINGS_MODULE'] = 'stats_core.settings'

application = get_wsgi_application()
