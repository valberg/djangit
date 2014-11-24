from django import template

import CommonMark

register = template.Library()

@register.filter
def commonmark(value):
    parser = CommonMark.DocParser()
    renderer = CommonMark.HTMLRenderer()
    ast = parser.parse(value)
    return renderer.render(ast)
