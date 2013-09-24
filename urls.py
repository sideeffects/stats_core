from django.conf.urls.defaults import patterns, include, url

# To use admin
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    
    # Enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
     # Add the houdini stats URLs.
    (r'', include('houdini_stats.urls')),
)