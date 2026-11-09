from django import template

register = template.Library()


@register.filter
def oferta(produto, campanha):
    """{% with o=produto|oferta:campanha %} → dict com pct, de, por, economia; ou None."""
    if not campanha:
        return None
    return campanha.oferta(produto)
