from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'src.views.home', name='home'),
    url(r'^auth', 'src.views.auth', name='auth'),
    url(r'^callback', 'src.views.callback', name='callback'),
    url(r'^logout$', 'src.views.logout', name='logout'),
    url(r'^admin/', include(admin.site.urls)),
)
