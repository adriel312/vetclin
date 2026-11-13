import uuid

from django.db import models


class TipoAtendimento(models.Model):
    """O que o cliente pode agendar pelo site (ex.: Consulta, Vacina)."""
    nome = models.CharField('Nome', max_length=60)
    descricao = models.CharField('Descrição curta', max_length=150, blank=True)
    icone = models.CharField('Ícone (Material Icons)', max_length=40, default='pets', blank=True)
    duracao = models.PositiveSmallIntegerField('Duração (minutos)', default=30)
    orientacoes = models.TextField(
        'Orientações extras', blank=True,
        help_text='Aparecem na confirmação, além das orientações gerais. Uma por linha.')
    ordem = models.PositiveSmallIntegerField('Ordem', default=0)
    ativo = models.BooleanField('Disponível no site', default=True)

    class Meta:
        verbose_name = 'Tipo de atendimento'
        verbose_name_plural = 'Tipos de atendimento'
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome

    def lista_orientacoes(self):
        return [l.strip() for l in self.orientacoes.splitlines() if l.strip()]


class HorarioFuncionamento(models.Model):
    """Faixas de horário em que o site oferece agendamentos.
    Para ter intervalo de almoço, cadastre duas faixas no mesmo dia (ex.: 08:00–12:00 e 14:00–18:00)."""
    DIAS = [(0, 'Segunda'), (1, 'Terça'), (2, 'Quarta'), (3, 'Quinta'), (4, 'Sexta'), (5, 'Sábado'), (6, 'Domingo')]
    dia_semana = models.PositiveSmallIntegerField('Dia da semana', choices=DIAS)
    abre = models.TimeField('Das')
    fecha = models.TimeField('Até')
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Horário de atendimento'
        verbose_name_plural = 'Horários de atendimento'
        ordering = ['dia_semana', 'abre']

    def __str__(self):
        return f'{self.get_dia_semana_display()} {self.abre:%H:%M}–{self.fecha:%H:%M}'


class Bloqueio(models.Model):
    """Dia sem agendamentos pelo site (feriado, folga, evento)."""
    data = models.DateField('Data', unique=True)
    motivo = models.CharField('Motivo', max_length=100, blank=True)

    class Meta:
        verbose_name = 'Dia bloqueado'
        verbose_name_plural = 'Dias bloqueados'
        ordering = ['data']

    def __str__(self):
        return f'{self.data:%d/%m/%Y} {self.motivo}'.strip()


class Agendamento(models.Model):
    PENDENTE, CONFIRMADO, CANCELADO, ATENDIDO = 'pendente', 'confirmado', 'cancelado', 'atendido'
    STATUS = [
        (PENDENTE, 'Aguardando confirmação'),
        (CONFIRMADO, 'Confirmado'),
        (CANCELADO, 'Cancelado'),
        (ATENDIDO, 'Atendido'),
    ]
    ESPECIES = [('cao', 'Cão'), ('gato', 'Gato'), ('outro', 'Outro')]
    OCUPA_HORARIO = (PENDENTE, CONFIRMADO)

    codigo = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    tipo = models.ForeignKey(TipoAtendimento, on_delete=models.PROTECT, verbose_name='Atendimento')
    data = models.DateField('Data')
    hora = models.TimeField('Horário')
    status = models.CharField('Situação', max_length=12, choices=STATUS, default=PENDENTE)

    tutor_nome = models.CharField('Nome do tutor', max_length=100)
    tutor_whatsapp = models.CharField('WhatsApp do tutor', max_length=20)
    tutor_email = models.EmailField('E-mail do tutor', blank=True)

    pet_nome = models.CharField('Nome do pet', max_length=60)
    especie = models.CharField('Espécie', max_length=10, choices=ESPECIES)
    raca = models.CharField('Raça', max_length=60, blank=True)
    idade = models.CharField('Idade', max_length=30, blank=True)
    peso = models.CharField('Peso aproximado', max_length=20, blank=True)
    primeira_vez = models.BooleanField('Primeira vez na clínica', default=False)

    sintomas = models.CharField('Sintomas marcados', max_length=400, blank=True)
    descricao = models.TextField('Descrição do tutor', blank=True)
    sinal_de_alerta = models.BooleanField('Marcou sintoma de alerta', default=False)

    consentimento = models.BooleanField('Autorizou o uso dos dados (LGPD)', default=False)
    observacao_interna = models.TextField('Observação interna', blank=True,
                                          help_text='Só a equipe vê.')
    criado_em = models.DateTimeField('Pedido feito em', auto_now_add=True)

    class Meta:
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'
        ordering = ['data', 'hora']
        indexes = [models.Index(fields=['data', 'status'])]

    def __str__(self):
        return f'{self.data:%d/%m} {self.hora:%H:%M} — {self.pet_nome} ({self.tipo})'

    @property
    def whatsapp_numero(self):
        import re
        d = re.sub(r'\D', '', self.tutor_whatsapp or '').lstrip('0')
        return d if d.startswith('55') else '55' + d
