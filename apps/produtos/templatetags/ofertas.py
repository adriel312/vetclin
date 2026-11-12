from django import template

register = template.Library()


@register.filter
def oferta(produto, campanha):
    """{% with o=produto|oferta:campanha %} → dict com pct, de, por, economia; ou None."""
    if not campanha:
        return None
    return campanha.oferta(produto)


@register.filter
def oferta_tamanho(tamanho, campanha):
    """Igual a "oferta", mas usando o preço de um tamanho específico."""
    if not campanha:
        return None
    return campanha.oferta(tamanho.produto, tamanho.preco)
