from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.text import truncate_words

class ForeignKeySearchInput(forms.HiddenInput):
    is_hidden = False
    """
    A Widget for displaying ForeignKeys in an autocomplete search input 
    instead in a <select> box.
    """
    class Media:
        css = {
            'all': ('extrafields/css/jquery.autocomplete.css',)
        }
        js = (
            'extrafields/js/jquery.js',
            'extrafields/js/jquery.autocomplete.js',
            'extrafields/js/AutocompleteObjectLookups.js',
        )

    def label_for_value(self, value):
        key = self.to_field_name or 'pk'
        rend = self.renderer_name or '__unicode__'
        instance = self.queryset.get(**{key: value})
        f = getattr(instance, self.renderer_name)
        if callable(f):
            f = f()
        return truncate_words(f, 14)
    
    def set_rel(self, rel):
        if rel is not None:
            self.to_field_name = rel.get_related_field().name
            self.queryset = rel.to._default_manager
    
    def set_search(self, search):
        if search is not None:
            self.to_field_name = search.extras.get('to_field_name')
            self.renderer_name = search.extras.get('renderer_name')
            self.search_fields = search.extras.get('search_fields')
            self.queryset = search.extras.get('queryset')
            self.search = search
    
    def __init__(self, search_fields=None, search=None, search_path=None, rel=None, queryset=None, 
                 renderer_name=None, to_field_name=None, required=True, attrs=None):
        super(ForeignKeySearchInput, self).__init__(attrs)
        self.set_search(search)
        self.search_path = search_path
        self.search_fields = search_fields
        self.queryset = queryset
        self.to_field_name = to_field_name
        self.renderer_name = renderer_name
        self.required = bool(required)
        self.set_rel(rel)

    def render(self, name, value, attrs=None):
        if self.search is None:
            for field in ['search_fields', 'queryset', 'search_path']:
                if getattr(self, field) is None:
                    raise Exception("Field %s shouldn't be None" % field)

        if attrs is None:
            attrs = {}

        rendered = super(ForeignKeySearchInput, self).render(name, value, attrs)
        
        if value in forms.fields.EMPTY_VALUES:
            label = u''
        else:
            try:
                label = self.label_for_value(value)
            except Exception, e:
                if not self.required:
                    label = value
                else:
                    raise
        
        extras = {}
        
        if not self.search:
            search_path = self.search_path
            opts = self.queryset.model._meta
            extras = {
                'search_fields': ','.join(self.search_fields),
                'search_path': self.search_path,
                'model_name': opts.module_name,
                'app_label': opts.app_label,
                'to_field_name': self.to_field_name or '',
                'renderer_name': self.renderer_name or '',
            }
        else:
            search_path = self.search.get_link()
            extras = self.search.render_extras()
        
        search_extras = '\n        '.join(["%s:'%s'" % (k,v) for k,v in extras.iteritems()])
            
        return rendered + mark_safe(u'''
<input type="text" id="lookup_%(name)s" value="%(label)s" size="40"/>
<script type="text/javascript">

function addItem_id_%(name)s(id, name) {
    $("#id_%(name)s").val( id );
    $("#lookup_%(name)s").val( name );
}

$(document).ready(function(){
function liFormat_%(name)s (row, i, num) {
    var result = row[0] ;
    return result;
}
function selectItem_%(name)s(li) {
    if( li == null ) var sValue = '';
    if( !!li.extra ) var sValue = li.extra[0];
    else var sValue = li.selectValue;
    if(sValue == undefined) sValue='';
    $("#id_%(name)s").val( sValue );
}

// --- Autocomplete ---
$("#lookup_%(name)s").autocomplete('%(search_path)s', {
    extraParams: {
        %(extras)s
    },
    delay:10,
    minChars:0,
    matchSubset:0,
    emptyAllowed:%(empty_allowed)s,
    autoFill:false,
    matchContains:1,
    cacheLength:10,
    selectFirst:false,
    formatItem:liFormat_%(name)s,
    maxItemsToShow:20,
    onItemSelect:selectItem_%(name)s
}); 
// --- Autocomplete ---
});
</script>

        ''') % {
            'MEDIA_URL': settings.MEDIA_URL,
            'empty_allowed': self.required and 'false' or 'true',
            'search_path': search_path,
            'extras': search_extras,
            'label': label,
            'name': name,
            'value': value,
        }

class ManyToManySearchInput(forms.MultipleHiddenInput):
    is_hidden=False
    """
    A Widget for displaying ForeignKeys in an autocomplete search input 
    instead in a <select> box.
    """
    class Media:
        css = {
            'all': ('extrafields/css/jquery.autocomplete.css',)
        }
        js = (
            'extrafields/js/jquery.js',
            'extrafields/js/jquery.autocomplete.js',
            'extrafields/js/AutocompleteObjectLookups.js ',
        )


    def set_rel(self, rel):
        if rel is not None:
            self.to_field_name = rel.get_related_field().name
            self.queryset = rel.to._default_manager
    
    def __init__(self, search_fields=None, search_path=None, rel=None, queryset=None, to_field_name=None, attrs=None):
        super(ManyToManySearchInput, self).__init__(attrs)
        self.search_path = search_path
        self.search_fields = search_fields
        self.queryset = queryset
        self.to_field_name = to_field_name
        self.help_text = ''
        self.set_rel(rel)

    def render(self, name, value, attrs=None):
        for field in ['search_fields', 'queryset', 'search_path', 'to_field_name']:
            value = getattr(self, field)
            if value is None:
                raise Exception("Field %s shouldn't be None" % field)
        
        if attrs is None:
            attrs = {}

        if value is None:
            value = []
        
        label = ''
        selected = ''
        for id in value:
            obj = self.queryset.get(id=id)

            selected = selected + mark_safe(u"""
                <div class="to_delete deletelink" ><input type="hidden" name="%(name)s" value="%(value)s"/>%(label)s</div>""" 
                )%{
                    'label': obj.name,
                    'name': name,
                    'value': obj.id,
        }

        opts = self.queryset.model._meta
        return mark_safe(u'''
<input type="text" id="lookup_%(name)s" value="" size="40"/>%(label)s
<div class="ac_chosen" style="padding-left:105px; width: 100%%">
<font style="color:#999999;font-size:10px !important;">%(help_text)s</font>
<div id="box_%(name)s" style="padding-left:20px;cursor:pointer;">

    %(selected)s
</div></div>

<script type="text/javascript">


function addItem_id_%(name)s(id,name) {
    // --- add element from popup ---
    $('<div class="to_delete deletelink"><input type="hidden" name="%(name)s" value="'+id+'"/>'+name+'</div>')
    .click(function () {$(this).remove();})
    .appendTo("#box_%(name)s");
    $("#lookup_%(name)s").val( '' );
}

$(document).ready(function(){
    $('#add_id_%(name)s').css("padding-left:105px;");
    
    function liFormat_%(name)s (row, i, num) {
        var result = row[0] ;
        return result;
    }
    function selectItem_%(name)s(li) {
        if( li == null ) return

        // --- create new element ---
        $('<div class="to_delete deletelink"><input type="hidden" name="%(name)s" value="'+li.extra[0]+'"/>'+li.selectValue+'</div>')
        .click(function () {$(this).remove();})
        .appendTo("#box_%(name)s");

        $("#lookup_%(name)s").val( '' );
    }

    // alert("#add_id_%(name)s");
    // alert($("#add_id_%(name)s"));

    // --- Autocomplete ---
    $("#lookup_%(name)s").autocomplete('%(search_path)s', {
        extraParams: {
            search_fields: '%(search_fields)s',
            app_label: '%(app_label)s',
            model_name: '%(model_name)s',
        },
        delay:10,
        minChars:0,
        matchSubset:1,
        autoFill:false,
        matchContains:1,
        cacheLength:10,
        selectFirst:true,
        formatItem:liFormat_%(name)s,
        maxItemsToShow:20,
        onItemSelect:selectItem_%(name)s
    }); 
// --- delete initial elements ---
    $(".to_delete").click(function () {$(this).remove();});
});
</script>

        ''') % {
            'search_fields': ','.join(self.search_fields),
            'search_path': self.search_path,
            'model_name': opts.module_name,
            'app_label': opts.app_label,
            'label': label,
            'name': name,
            'value': value,
            'selected':selected,
            'help_text':self.help_text
        }
