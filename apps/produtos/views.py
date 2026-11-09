from django.shortcuts import render, get_object_or_404
from .models import Campanha, Categoria, Produto


def lista(request):
    categorias = Categoria.objects.all()
    categoria_slug = request.GET.get('categoria')
    produtos = Produto.objects.filter(ativo=True).select_related('categoria')
    if categoria_slug:
        produtos = produtos.filter(categoria__slug=categoria_slug)

    campanha = Campanha.atual()
    em_oferta, demais = [], []
    if campanha:
        for p in produtos:
            p.oferta = campanha.oferta(p)
            (em_oferta if p.oferta else demais).append(p)

    context = {
        'produtos': produtos,
        'em_oferta': em_oferta,
        'demais': demais,
        'categorias': categorias,
        'categoria_ativa': categoria_slug,
    }
    try:
        from apps.planos.models import Plano
        context['plano_menor_preco'] = Plano.objects.filter(ativo=True).order_by('preco_mensal').values_list(
            'preco_mensal', flat=True).first()
    except Exception:
        pass
    return render(request, 'pages/produtos.html', context)


def detalhe(request, slug):
    produto = get_object_or_404(Produto, slug=slug, ativo=True)
    relacionados = Produto.objects.filter(categoria=produto.categoria, ativo=True).exclude(pk=produto.pk)[:4]
    return render(request, 'pages/produto_detalhe.html', {'produto': produto, 'relacionados': relacionados})
