from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from views import search

urlpatterns = patterns('',
    url(r'^$', search, {}, 'extrafields_autocomplete'),
)
