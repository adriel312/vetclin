"""Cadastra os planos do Clube Preventivo e as perguntas iniciais.
Só cria se ainda não houver nenhum plano, então não sobrescreve edições feitas no painel."""
from decimal import Decimal

from django.db import migrations

PLANOS = [
    {
        'nome': 'Essencial', 'slug': 'essencial', 'preco': '49.00', 'destaque': False,
        'subtitulo': 'Cuidado preventivo para o dia a dia',
        'incluso': [
            '2 consultas por ano',
            'Consultas adicionais com coparticipação de R$ 90,00',
        ],
        'desconto': [
            ('Exames laboratoriais', '20%'),
            ('Ultrassom', '20%'),
            ('Vacinas', '15%'),
            ('Cirurgias gerais*', '10%'),
            ('Internação (até 2 diárias)', '10%'),
        ],
        'adicional': [
            'Lembrete de vacinas',
            'Acompanhamento preventivo básico',
            'Prioridade leve em encaixes',
        ],
    },
    {
        'nome': 'Prevent', 'slug': 'prevent', 'preco': '89.00', 'destaque': True,
        'subtitulo': 'Consultas ilimitadas e acompanhamento contínuo',
        'incluso': [
            'Consultas ilimitadas com coparticipação de R$ 55,00',
            '1 hemograma por ano',
        ],
        'desconto': [
            ('Exames', '25%'),
            ('Vacinas', '20%'),
            ('Cirurgias*', '15%'),
            ('Internação (até 2 diárias)', '20%'),
        ],
        'adicional': [
            'Prioridade de atendimento',
            'Encaixe preferencial',
            'Lembretes completos (vacinas e retornos)',
            'Acompanhamento preventivo contínuo',
        ],
    },
    {
        'nome': 'Premium', 'slug': 'premium', 'preco': '149.00', 'destaque': False,
        'subtitulo': 'Check-up completo e prioridade máxima',
        'incluso': [
            'Consultas ilimitadas com coparticipação de R$ 40,00',
            '1 hemograma por ano',
            '1 perfil bioquímico por ano',
            '1 ultrassom por ano',
        ],
        'desconto': [
            ('Exames', '30%'),
            ('Vacinas', '30%'),
            ('Cirurgias*', '20%'),
            ('Internação (sem limite de diárias)', '30%'),
        ],
        'adicional': [
            'Atendimento prioritário máximo',
            'Encaixe garantido (quando possível)',
            'Check-up preventivo anual incluso',
            'Gestão completa da saúde do pet',
        ],
    },
]

PERGUNTAS = [
    ('O que é coparticipação?',
     'É um valor reduzido que você paga a cada consulta, além da mensalidade. '
     'No Essencial, 2 consultas por ano já estão inclusas e as adicionais custam R$ 90,00. '
     'No Prevent e no Premium as consultas são ilimitadas, com coparticipação de R$ 55,00 e R$ 40,00.'),
    ('Os descontos valem para qualquer cirurgia?',
     'Os descontos em cirurgias aplicam-se exclusivamente a procedimentos eletivos e de baixa complexidade. '
     'Cirurgias de maior complexidade serão avaliadas individualmente.'),
    ('Como funciona o desconto na internação?',
     'No Essencial o desconto é de 10% em até 2 diárias e no Prevent, de 20% em até 2 diárias. '
     'No Premium o desconto é de 30%, independente de quantos dias o pet fique internado.'),
    ('Como faço para assinar?',
     'Fale com a nossa equipe pelo WhatsApp ou na recepção da clínica. '
     'Fazemos o cadastro do seu pet e explicamos todas as condições do contrato.'),
]


def criar(apps, schema_editor):
    Plano = apps.get_model('planos', 'Plano')
    Beneficio = apps.get_model('planos', 'Beneficio')
    Pergunta = apps.get_model('planos', 'PerguntaFrequente')
    Pagina = apps.get_model('planos', 'PaginaPlano')

    if not Pagina.objects.exists():
        Pagina.objects.create()

    if Plano.objects.exists():
        return
    for ordem, d in enumerate(PLANOS, start=1):
        plano = Plano.objects.create(nome=d['nome'], slug=d['slug'], subtitulo=d['subtitulo'],
                                     preco_mensal=Decimal(d['preco']), destaque=d['destaque'], ordem=ordem)
        n = 0
        for texto in d['incluso']:
            Beneficio.objects.create(plano=plano, grupo='incluso', texto=texto, ordem=n); n += 1
        for texto, valor in d['desconto']:
            Beneficio.objects.create(plano=plano, grupo='desconto', texto=texto, valor=valor, ordem=n); n += 1
        for texto in d['adicional']:
            Beneficio.objects.create(plano=plano, grupo='adicional', texto=texto, ordem=n); n += 1

    if not Pergunta.objects.exists():
        for ordem, (p, r) in enumerate(PERGUNTAS):
            Pergunta.objects.create(pergunta=p, resposta=r, ordem=ordem)


class Migration(migrations.Migration):
    dependencies = [('planos', '0001_initial')]
    operations = [migrations.RunPython(criar, migrations.RunPython.noop)]
