from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key) 
@register.filter
def add_error_class(field):
    css_classes = field.field.widget.attrs.get('class', '')
    if 'form-control' not in css_classes and field.field.widget.__class__.__name__ != 'Select':
        css_classes += ' form-control'
    if 'form-select' not in css_classes and field.field.widget.__class__.__name__ == 'Select':
        css_classes += ' form-select'
    if field.errors:
        css_classes += ' is-invalid'
    return field.as_widget(attrs={'class': css_classes.strip()})