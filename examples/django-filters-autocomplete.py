#FIXME: imports missing

class DomainSearch(CompletionProvider):
    domains = CompletionSource(queryset=Domain.objects.filter(public=True),
                     search_fields=['^name'],
                     to_field_name='name',
                     renderer_name='name')

    templates = CompletionSource(queryset=Domain.objects.filter(public=True),
                       search_fields=['^template'],
                       to_field_name='template',
                       renderer_name='template')

    keywords = CompletionSource(queryset=Keyword.objects,
                      search_fields=['^keyword'],
                      to_field_name='keyword',
                      renderer_name='keyword')

class ForeignKeyFilter(Filter):
    field_class = ForeignKeyFormField

class DomainsFilterSet(FilterSet):
    #date = DateFilter(widget=AdminDateInput)
    country = ChoiceFilter(name='country')
    domain = ForeignKeyFilter(name='domain__name', lookup_type='startswith', search=DomainSearch.domains)
    template = ForeignKeyFilter(name='domain__template', lookup_type='startswith', search=DomainSearch.templates)
    keywords = ForeignKeyFilter(name='domain__keywords__keyword', lookup_type='exact', search=DomainSearch.keywords)
    period = ChoiceFilter(choices=PERIODS)
    group = ModelChoiceFilter(name='domain__groups', 
                              queryset=Group.objects, empty_label='Any domain')
    
    def __init__(self, *args, **kw):
        super(DomainsFilterSet, self).__init__(*args, **kw)
        #country = self.filters['country']
        #country.field.choices = country_choices()

urlpatterns = patterns('',
    (r'^domains/complete/', include(domains.DomainSearch.get_urls())),
)
