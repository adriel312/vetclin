"""Cadastra a Black Friday 2026 (22/11 a 29/11) com os produtos do design.
Tudo pode ser ajustado depois no painel, em Loja → Black Friday / Campanhas."""
from datetime import datetime
from zoneinfo import ZoneInfo

from django.db import migrations

FUSO = ZoneInfo('America/Sao_Paulo')
TERMOS = ['NexGard Spectra', 'Golden', 'Frontmax']


def criar(apps, schema_editor):
    Campanha = apps.get_model('produtos', 'Campanha')
    ItemCampanha = apps.get_model('produtos', 'ItemCampanha')
    Produto = apps.get_model('produtos', 'Produto')
    if Campanha.objects.filter(nome='Black Friday').exists():
        return
    campanha = Campanha.objects.create(
        nome='Black Friday',
        frase_faixa='Até 15% OFF em produtos selecionados da loja',
        inicio=datetime(2026, 11, 22, 0, 0, tzinfo=FUSO),
        fim=datetime(2026, 11, 29, 23, 59, 59, tzinfo=FUSO),
        desconto_padrao=15,
        toda_loja=False,
    )
    vistos = set()
    for termo in TERMOS:
        for produto in Produto.objects.filter(nome__icontains=termo, ativo=True):
            if produto.pk not in vistos:
                ItemCampanha.objects.create(campanha=campanha, produto=produto)
                vistos.add(produto.pk)


class Migration(migrations.Migration):
    dependencies = [('produtos', '0002_campanhas')]
    operations = [migrations.RunPython(criar, migrations.RunPython.noop)]
