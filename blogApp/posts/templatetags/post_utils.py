from django.template import Library
import urllib
register = Library()


@register.filter
def get_range(value):
    return range(value)


@register.filter
def to_str(value):
    return str(value)


@register.simple_tag
def q_string(**kwargs):
    result = {}
    for k, v in kwargs.items():
        if v is not None:
            result[k] = v
    return "?" + urllib.urlencode(result)


@register.simple_tag
def post_content(post):
    return post.formated_content()
