from django import forms
from widgets import ForeignKeySearchInput, ManyToManySearchInput


class ForeignKeyFormField(forms.CharField):
    widget = ForeignKeySearchInput

    def __init__(self, search_fields=None, queryset=None, search_path=None, search=None,
                 to_field_name=None, renderer_name=None, required=True, *args, **kwargs):

        base = super(ForeignKeyFormField, self)
        base.__init__(self, required=required, *args, **kwargs)
        
        self.widget.set_search(search)
        self.widget.search_fields = search_fields
        self.widget.search_path = search_path
        self.widget.to_field_name = to_field_name
        self.widget.queryset = queryset
        self.widget.renderer_name = renderer_name
        self.widget.required = required

class ManyToManyFormField(forms.CharField):
    widget = ManyToManySearchInput

    def __init__(self, search_fields=None, queryset=None, search_path=None, search=None,
                 to_field_name=None, renderer_name=None, required=True, help_text='', *args, **kwargs):

        base = super(ManyToManyFormField, self)
        base.__init__(self, *args, **kwargs)
        
        self.widget.set_search(search)
        self.widget.search_fields = search_fields
        self.widget.search_path = search_path
        self.widget.to_field_name = to_field_name
        self.widget.queryset = queryset
        self.widget.renderer_name = renderer_name
        self.widget.required = required
        self.widget.help_text = help_text
