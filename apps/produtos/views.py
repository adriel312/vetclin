from django.shortcuts import render, get_object_or_404
from .models import Produto, Categoria


def lista(request):
    categorias = Categoria.objects.prefetch_related('produtos')
    categoria_slug = request.GET.get('categoria')
    produtos = Produto.objects.filter(ativo=True).select_related('categoria')
    if categoria_slug:
        produtos = produtos.filter(categoria__slug=categoria_slug)
    context = {
        'produtos': produtos,
        'categorias': categorias,
        'categoria_ativa': categoria_slug,
    }
    return render(request, 'pages/produtos.html', context)


def detalhe(request, slug):
    produto = get_object_or_404(Produto, slug=slug, ativo=True)
    relacionados = Produto.objects.filter(categoria=produto.categoria, ativo=True).exclude(pk=produto.pk)[:4]
    return render(request, 'pages/produto_detalhe.html', {'produto': produto, 'relacionados': relacionados})
