"""Cálculo dos horários livres para agendar pelo site."""
from datetime import date, datetime, timedelta

from django.utils import timezone

from .models import Agendamento, Bloqueio, HorarioFuncionamento

ANTECEDENCIA_MINIMA = timedelta(hours=2)   # não deixa marcar para daqui a menos de 2 horas
DIAS_A_FRENTE = 21                          # mostra as próximas 3 semanas
INTERVALO_MAXIMO = 30                       # horários oferecidos a cada 30 min no máximo


def _agora():
    return timezone.localtime()


def horarios_livres(tipo, dia):
    """Lista de horários (time) livres para o tipo de atendimento no dia."""
    if dia < _agora().date() or Bloqueio.objects.filter(data=dia).exists():
        return []
    faixas = HorarioFuncionamento.objects.filter(dia_semana=dia.weekday(), ativo=True)
    if not faixas:
        return []

    duracao = timedelta(minutes=tipo.duracao)
    passo = timedelta(minutes=min(tipo.duracao, INTERVALO_MAXIMO))
    limite = _agora() + ANTECEDENCIA_MINIMA
    fuso = timezone.get_current_timezone()

    ocupados = []
    for ag in Agendamento.objects.filter(data=dia, status__in=Agendamento.OCUPA_HORARIO).select_related('tipo'):
        ini = datetime.combine(dia, ag.hora)
        ocupados.append((ini, ini + timedelta(minutes=ag.tipo.duracao)))

    livres = []
    for faixa in faixas:
        inicio = datetime.combine(dia, faixa.abre)
        fim_faixa = datetime.combine(dia, faixa.fecha)
        while inicio + duracao <= fim_faixa:
            fim = inicio + duracao
            futuro = timezone.make_aware(inicio, fuso) >= limite
            conflito = any(inicio < o_fim and o_ini < fim for o_ini, o_fim in ocupados)
            if futuro and not conflito:
                livres.append(inicio.time())
            inicio += passo
    return sorted(set(livres))


def proximos_dias():
    """Dias dos próximos DIAS_A_FRENTE em que a clínica atende pelo site (sem olhar ocupação)."""
    hoje = _agora().date()
    dias_semana = set(HorarioFuncionamento.objects.filter(ativo=True).values_list('dia_semana', flat=True))
    bloqueados = set(Bloqueio.objects.filter(data__gte=hoje).values_list('data', flat=True))
    dias = []
    for i in range(DIAS_A_FRENTE + 1):
        d = hoje + timedelta(days=i)
        if d.weekday() in dias_semana and d not in bloqueados:
            dias.append(d)
    return dias


def esta_livre(tipo, dia: date, hora):
    return hora in horarios_livres(tipo, dia)
