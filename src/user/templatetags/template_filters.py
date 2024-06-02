from django.forms.models import model_to_dict
from django.template.defaulttags import register

@register.filter
def get_item(dictionary, key):
    return model_to_dict(dictionary, fields=[field.name for field in dictionary._meta.fields]).get(key)
