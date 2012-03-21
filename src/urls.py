from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'raised.views.home', name='home'),
    url(r'^auth', 'raised.views.auth', name='auth'),
    url(r'^callback', 'raised.views.callback', name='callback'),
    url(r'^logout$', 'raised.views.logout', name='logout'),
    url(r'^admin/', include(admin.site.urls)),
)
