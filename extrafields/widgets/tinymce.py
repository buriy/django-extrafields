from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

class TinyMCEEditor(forms.Textarea):
    class Media:
        js = (
            'extrafields/js/jquery.js',
            'extrafields/tiny_mce/jquery.tinymce.js',
        )

    def render(self, name, value, attrs=None):
        rendered = super(TinyMCEEditor, self).render(name, value, attrs)
        return rendered + mark_safe(u"""<script type="text/javascript">
        alert('running js at #id_%s');
    jQuery('#id_%s').tinymce({
        script_url : '%sextrafields/tiny_mce/tiny_mce.js',
        mode : "textareas",
        convert_urls : false,
        width:  585,
        height: 380,
        theme : "advanced",
        plugins : "table,searchreplace",
        theme_advanced_buttons1 : "bold,italic,underline,separator,link,unlink,image,strikethrough,separator,bullist,numlist,separator,indent,outdent,separator,justifyleft,justifycenter,justifyright,justifyfull,separator,undo,redo,separator,formatselect,separator,search,replace,separator,code",
        theme_advanced_buttons2 : "tablecontrols",
        theme_advanced_buttons3 : "",
        theme_advanced_toolbar_location : "top",
        theme_advanced_toolbar_align : "left",
        theme_advanced_path_location : "bottom",
        extended_valid_elements : "a[name|href|target|title|onclick]"
    });
</script>""" % (name, name, settings.MEDIA_URL))
