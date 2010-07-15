from django.db import models
from django.http import HttpResponse
from django.http import HttpResponseBadRequest

def construct_search(field_name):
    # use different lookup methods depending on the notation
    if field_name.startswith('^'):
        return "%s__istartswith" % field_name[1:]
    elif field_name.startswith('='):
        return "%s__iexact" % field_name[1:]
    elif field_name.startswith('@'):
        return "%s__search" % field_name[1:]
    else:
        return "%s__icontains" % field_name

def filter_search(queryset, search_fields, query):
    q = None
    for field_name in search_fields:
        name = construct_search(field_name)

        if q:
            q = q | models.Q( **{str(name):query} )
        else:
            q = models.Q( **{str(name):query} )

    qs = queryset.filter( q )
    return qs

def get_and_apply(instance, field):
    f = getattr(instance, field)
    if callable(f):
        return f()
    return f

def complete_query(query, queryset, search_fields, to_field_name=None, renderer_name=None, limit=None):
    
    # print 'Complete query:', query, queryset, search_fields, to_field_name, renderer_name, limit
    #       Searches in the fields of the given related model and returns the 
    #       result as a simple string to be used by the jQuery Autocomplete plugin
    
    if to_field_name is None:
        to_field_name = 'pk'

    if renderer_name is None:
        renderer_name = '__unicode__'

    #print '-----------------------'
    #print search_fields, app_label, model_name, query
    
    try:
        limit = int(limit)
    except ValueError:
        return HttpResponseBadRequest() 

    if not search_fields:
        return HttpResponseBadRequest("Bad search_fields")
    if queryset is None:
        return HttpResponseBadRequest("Bad queryset")
    if query is None:
        return HttpResponseBadRequest("Bad query")

    qs = filter_search(queryset, search_fields, query).order_by(to_field_name)
    
    #filter only unique choices
    choices = []
    choicesset = set()
    for f in qs[:limit]:
        name = get_and_apply(f, renderer_name).replace('|','-')
        key  = get_and_apply(f, to_field_name)
        result = u'%s|%s\n' % (name, key)
        if not result in choicesset:
            choices.append(result)
            choicesset.add(result)
    data = ''.join(choices)
    return HttpResponse(data, mimetype='text/plain')


def complete(request, queryset=None, search_fields=None, to_field_name=None, renderer_name=None):
    
    #       Searches in the fields of the given related model and returns the 
    #       result as a simple string to be used by the jQuery Autocomplete plugin
    
    # print 'Complete request:', queryset, search_fields, to_field_name, renderer_name
    
    query = request.GET.get('q', '')

    if queryset is None:
        app_label = request.GET.get('app_label', None)
        model_name = request.GET.get('model_name', None)
        model = models.get_model(app_label, model_name)
        queryset = model.objects
        
    if search_fields is None:
        search_fields = request.GET.get('search_fields', '').split(',')
        
    if to_field_name is None:
        to_field_name = request.GET.get('to_field_name', None)

    if renderer_name is None:
        renderer_name = request.GET.get('renderer_name', None)

    limit = request.GET.get('limit', 100)

    return complete_query(query, queryset, search_fields, to_field_name, renderer_name, limit=limit)
