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

def filter_search(model, search_fields, query):
    q = None
    for field_name in search_fields.split(','):
        name = construct_search(field_name)

        if q:
            q = q | models.Q( **{str(name):query} )
        else:
            q = models.Q( **{str(name):query} )

    qs = model.objects.filter( q )
    return qs

def get_and_apply(instance, field):
    f = getattr(instance, field)
    if callable(f):
        return f()
    return f

def search(request, **filters):
    
    #       Searches in the fields of the given related model and returns the 
    #       result as a simple string to be used by the jQuery Autocomplete plugin
    
    query = request.GET.get('q', '')

    app_label = request.GET.get('app_label', None)
    model_name = request.GET.get('model_name', None)
    search_fields = request.GET.get('search_fields', None)
    to_field_name = request.GET.get('to_field_name', None) or 'pk'
    renderer_name = request.GET.get('renderer_name', None) or '__unicode__'

    #print '-----------------------'
    #print search_fields, app_label, model_name, query
    
    limit = request.GET.get('limit', 10000)
    try:
        limit = int(limit)
    except ValueError:
        return HttpResponseBadRequest() 

    if not search_fields or not app_label or not model_name or query is None:
        return HttpResponseBadRequest()

    model = models.get_model(app_label, model_name)
    qs = filter_search(model, search_fields, query).filter(**filters).order_by(to_field_name)
    
    choices = []
    for f in qs[:limit]:
        name = get_and_apply(f, renderer_name)
        key  = get_and_apply(f, to_field_name)
        choices.append(u'%s|%s\n' % (name, key))
    data = ''.join(choices)
    return HttpResponse(data, mimetype='text/plain')
