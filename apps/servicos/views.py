from django.shortcuts import render, get_object_or_404
from .models import Servico


def lista(request):
    servicos = Servico.objects.filter(ativo=True)
    return render(request, 'pages/servicos.html', {'servicos': servicos})


def detalhe(request, slug):
    servico = get_object_or_404(Servico, slug=slug, ativo=True)
    return render(request, 'pages/servico_detalhe.html', {'servico': servico})
