from django.conf.urls.defaults import url
from django.core.urlresolvers import reverse 
from django.utils.datastructures import SortedDict
from static import Static
from views import complete

class CompletionSource(object):
    def __init__(self, **kwargs):
        self.extras = kwargs
        #self.complete = lambda request: complete(request, **self.extras)
    
    def contribute_to_class(self, cls, name):
        cls.pages[name] = self
        setattr(cls, name, self)

    def get_link(self):
        return reverse(complete)
    
    def render_extras(self):
        return {}
    
class CompletionProvider(Static):
    def _new_(self, attrs, parents):
        self.pages = SortedDict()
        for name, attr in attrs.iteritems():
            self._add_to_class_(name, attr)

    def __new__(self, page):
        return self.pages[page]()
    
    def get_urls(self):
        urls = [url('^'+k+'/$', complete, v.extras) for k,v in self.pages.iteritems()]
#        print 'Urls:', ["%s -> %s" % (u.regex, unicode(u.default_args)) for u in urls] 
        return urls
