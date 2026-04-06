from django.shortcuts import render
from .models import Membro
from apps.produtos.models import Produto
from apps.servicos.models import Servico
from apps.exames.models import Exame


def home(request):
    context = {
        'servicos_destaque': Servico.objects.filter(destaque=True, ativo=True)[:6],
        'produtos_destaque': Produto.objects.filter(destaque=True, ativo=True)[:8],
        'equipe': Membro.objects.filter(ativo=True),
    }
    return render(request, 'pages/home.html', context)


def sobre(request):
    context = {'equipe': Membro.objects.filter(ativo=True)}
    return render(request, 'pages/sobre.html', context)
