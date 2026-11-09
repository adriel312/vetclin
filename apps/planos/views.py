from django.db.models import Prefetch
from django.shortcuts import render
from .models import PaginaPlano, Plano, Beneficio, PerguntaFrequente


def lista(request):
    planos = list(Plano.objects.filter(ativo=True)
                  .prefetch_related(Prefetch('beneficios', queryset=Beneficio.objects.order_by('ordem', 'id'))))
    return render(request, 'pages/plano.html', {
        'pagina': PaginaPlano.objects.first(),
        'planos': planos,
        'perguntas': PerguntaFrequente.objects.filter(ativo=True),
        'menor_preco': min((p.preco_mensal for p in planos), default=None),
    })
