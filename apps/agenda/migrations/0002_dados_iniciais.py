"""Cadastra os atendimentos agendáveis e os horários iniciais. Tudo pode ser mudado no painel."""
from datetime import time

from django.db import migrations

TIPOS = [
    ('Consulta', 'Avaliação clínica completa com o veterinário.', 'medical_services', 30, 1,
     'Se puder, anote quando os sintomas começaram e o que o pet comeu nos últimos dias.'),
    ('Vacina', 'Aplicação de vacinas e revisão da carteira.', 'vaccines', 15, 2,
     'O pet precisa estar saudável no dia (sem febre, vômito ou diarreia).\n'
     'Traga a carteira de vacinação para registrarmos a nova dose.'),
]
HORARIOS = [(d, time(8), time(18)) for d in range(5)] + [(5, time(8), time(12))]


def criar(apps, schema_editor):
    Tipo = apps.get_model('agenda', 'TipoAtendimento')
    Horario = apps.get_model('agenda', 'HorarioFuncionamento')
    if not Tipo.objects.exists():
        for nome, desc, icone, dur, ordem, orient in TIPOS:
            Tipo.objects.create(nome=nome, descricao=desc, icone=icone, duracao=dur, ordem=ordem, orientacoes=orient)
    if not Horario.objects.exists():
        for dia, abre, fecha in HORARIOS:
            Horario.objects.create(dia_semana=dia, abre=abre, fecha=fecha)


class Migration(migrations.Migration):
    dependencies = [('agenda', '0001_initial')]
    operations = [migrations.RunPython(criar, migrations.RunPython.noop)]
