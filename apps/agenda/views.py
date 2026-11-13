from datetime import date

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .disponibilidade import horarios_livres, proximos_dias
from .forms import SINAIS_DE_ALERTA, SINTOMAS, AgendamentoForm
from .models import Agendamento, TipoAtendimento

ORIENTACOES_GERAIS = [
    'Leve a carteira de vacinação do pet.',
    'Leve o histórico médico: exames, receitas e laudos anteriores.',
    'Anote os remédios que o pet usa ou leve as embalagens.',
    'Cães na guia ou no colo; gatos sempre na caixa de transporte.',
    'Chegue com 10 minutos de antecedência.',
]


def agendar(request):
    form = AgendamentoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        d = form.cleaned_data
        with transaction.atomic():
            # confere de novo dentro da transação, para dois clientes não pegarem o mesmo horário
            if d['hora'] not in horarios_livres(d['tipo'], d['data']):
                form.add_error('hora', 'Esse horário acabou de ser ocupado. Escolha outro, por favor.')
            else:
                ag = Agendamento.objects.create(
                    tipo=d['tipo'], data=d['data'], hora=d['hora'],
                    tutor_nome=d['tutor_nome'], tutor_whatsapp=d['tutor_whatsapp'], tutor_email=d['tutor_email'],
                    pet_nome=d['pet_nome'], especie=d['especie'], raca=d['raca'], idade=d['idade'], peso=d['peso'],
                    primeira_vez=d['primeira_vez'], sintomas=', '.join(d['sintomas']), descricao=d['descricao'],
                    sinal_de_alerta=form.tem_alerta, consentimento=True,
                )
                _avisar_clinica(request, ag)
                return redirect('agenda:pedido', codigo=ag.codigo)

    tipos = TipoAtendimento.objects.filter(ativo=True)
    return render(request, 'pages/agendar.html', {
        'form': form,
        'tipos': tipos,
        'dias': proximos_dias(),
        'sintomas': SINTOMAS,
        'sinais_alerta': SINAIS_DE_ALERTA,
        'marcados': form['sintomas'].value() or [],
        'tem_alerta': any(s in {v for v, _ in SINAIS_DE_ALERTA} for s in (form['sintomas'].value() or [])),
        'especies': Agendamento.ESPECIES,
        'valores': {nome: form[nome].value() for nome in form.fields},
        'horarios': _horarios_do_post(form),
    })


def _horarios_do_post(form):
    """Ao reexibir o formulário com erro, já mostra os horários do dia escolhido."""
    try:
        tipo = TipoAtendimento.objects.get(pk=form['tipo'].value())
        dia = date.fromisoformat(form['data'].value())
        return horarios_livres(tipo, dia)
    except Exception:
        return None


def horarios(request):
    """Trecho de página com os horários livres (carregado pelo HTMX ao escolher tipo e dia)."""
    livres, erro = [], ''
    try:
        tipo = TipoAtendimento.objects.get(pk=request.GET.get('tipo'), ativo=True)
        dia = date.fromisoformat(request.GET.get('data', ''))
        livres = horarios_livres(tipo, dia)
    except (TipoAtendimento.DoesNotExist, ValueError):
        erro = 'Escolha o atendimento e o dia para ver os horários.'
    return render(request, 'partials/agenda_horarios.html', {
        'horarios': livres, 'erro': erro, 'hora_escolhida': request.GET.get('hora', ''),
    })


def pedido(request, codigo):
    ag = get_object_or_404(Agendamento.objects.select_related('tipo'), codigo=codigo)
    return render(request, 'pages/agendar_ok.html', {
        'ag': ag,
        'orientacoes': ORIENTACOES_GERAIS + ag.tipo.lista_orientacoes(),
    })


def _avisar_clinica(request, ag):
    destino = getattr(settings, 'CONTACT_EMAIL', '')
    if not destino:
        return
    alerta = '⚠ MARCOU SINAL DE ALERTA\n\n' if ag.sinal_de_alerta else ''
    send_mail(
        subject=f'[Agenda] {ag.tipo} — {ag.pet_nome} — {ag.data:%d/%m} {ag.hora:%H:%M}',
        message=(
            f'{alerta}Novo pedido de agendamento pelo site (aguardando confirmação).\n\n'
            f'Atendimento: {ag.tipo}\nData: {ag.data:%d/%m/%Y} às {ag.hora:%H:%M}\n\n'
            f'Pet: {ag.pet_nome} ({ag.get_especie_display()}) {ag.raca} · {ag.idade} · {ag.peso}\n'
            f'Primeira vez: {"sim" if ag.primeira_vez else "não"}\n'
            f'Sintomas: {ag.sintomas or "—"}\nDescrição: {ag.descricao or "—"}\n\n'
            f'Tutor: {ag.tutor_nome}\nWhatsApp: {ag.tutor_whatsapp}\nE-mail: {ag.tutor_email or "—"}\n\n'
            f'Confirme no painel: {request.build_absolute_uri("/admin/agenda/agendamento/")}'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[destino],
        fail_silently=True,
    )
