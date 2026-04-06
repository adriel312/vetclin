from django.shortcuts import render
from .models import GrupoExame


def lista(request):
    grupos = GrupoExame.objects.prefetch_related('exames').all()
    return render(request, 'pages/exames.html', {'grupos': grupos})
