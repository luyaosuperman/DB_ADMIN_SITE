from django import template
from db_survey.forms import *

register = template.Library()

def key(d, key_name):
    try:
        return d[key_name]
    except:
        return 'KEY_TOBE_IGNORED'
key = register.filter('key', key)

def row_span_of_key(d, key_name):
    return d[key_name + '_rowspan']
row_span_of_key = register.filter('row_span_of_key', row_span_of_key)

def get_attr_of_form(form_name,attr_name):
    #cd = form_name.cleaned_data
    #try:
        return form_name.cleaned_data[attr_name]
    #except:
    #    return 'KEY_TOBE_IGNORED'
get_attr_of_form = register.filter('get_attr_of_form', get_attr_of_form)
