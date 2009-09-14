from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from views import complete

urlpatterns = patterns('',
    url(r'^$', complete, {}, 'extrafields_autocomplete'),
)
