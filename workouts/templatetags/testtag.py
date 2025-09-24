from django import template
register = template.Library()

@register.simple_tag
def hellotag():
    return "HELLO TAG"
