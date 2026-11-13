from urllib.parse import quote

from django.contrib import admin, messages
from django.utils import timezone
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from .models import Agendamento, Bloqueio, HorarioFuncionamento, TipoAtendimento


def _link_whatsapp(ag, texto):
    return f'https://wa.me/{ag.whatsapp_numero}?text={quote(texto)}'


def _msg_confirmacao(ag):
    return (f'Olá, {ag.tutor_nome.split()[0]}! Aqui é da Vet Clin 🐾\n'
            f'Seu agendamento de {ag.tipo} para {ag.pet_nome} está CONFIRMADO para '
            f'{ag.data:%d/%m} às {ag.hora:%H:%M}.\n'
            f'Lembre de trazer a carteira de vacinação e o histórico médico do pet. Até lá!')


def _msg_remarcar(ag):
    return (f'Olá, {ag.tutor_nome.split()[0]}! Aqui é da Vet Clin 🐾\n'
            f'Recebemos o pedido de {ag.tipo} para {ag.pet_nome} em {ag.data:%d/%m} às {ag.hora:%H:%M}, '
            f'mas esse horário não está disponível. Podemos combinar outro?')


class HojeEmDianteFilter(admin.SimpleListFilter):
    title = 'período'
    parameter_name = 'periodo'

    def lookups(self, request, model_admin):
        return [('hoje', 'Hoje'), ('proximos', 'De hoje em diante'), ('passados', 'Passados')]

    def queryset(self, request, qs):
        hoje = timezone.localdate()
        if self.value() == 'hoje':
            return qs.filter(data=hoje)
        if self.value() == 'proximos':
            return qs.filter(data__gte=hoje)
        if self.value() == 'passados':
            return qs.filter(data__lt=hoje)
        return qs


@admin.register(Agendamento)
class AgendamentoAdmin(ModelAdmin):
    list_display = ('quando', 'pet', 'tipo', 'tutor_nome', 'alerta', 'status', 'whatsapp')
    list_editable = ('status',)
    list_filter = ('status', HojeEmDianteFilter, 'tipo', 'sinal_de_alerta')
    list_display_links = ('quando', 'pet')
    search_fields = ('pet_nome', 'tutor_nome', 'tutor_whatsapp')
    date_hierarchy = 'data'
    ordering = ('data', 'hora')
    actions = ['marcar_confirmado', 'marcar_atendido', 'marcar_cancelado']
    readonly_fields = ('criado_em', 'consentimento', 'botoes_whatsapp')
    fieldsets = (
        ('Atendimento', {'fields': ('status', 'tipo', 'data', 'hora', 'botoes_whatsapp')}),
        ('Pet', {'fields': ('pet_nome', 'especie', 'raca', 'idade', 'peso', 'primeira_vez')}),
        ('Motivo da visita', {'fields': ('sinal_de_alerta', 'sintomas', 'descricao')}),
        ('Tutor', {'fields': ('tutor_nome', 'tutor_whatsapp', 'tutor_email', 'consentimento')}),
        ('Equipe', {'fields': ('observacao_interna', 'criado_em')}),
    )

    def changelist_view(self, request, extra_context=None):
        # Abre mostrando "de hoje em diante" na primeira visita
        if not request.GET and 'periodo' not in request.GET:
            q = request.GET.copy(); q['periodo'] = 'proximos'
            request.GET = q; request.META['QUERY_STRING'] = q.urlencode()
        return super().changelist_view(request, extra_context)

    @admin.display(description='Quando', ordering='data')
    def quando(self, obj):
        return f'{obj.data:%d/%m} {obj.hora:%H:%M}'

    @admin.display(description='Pet')
    def pet(self, obj):
        return f'{obj.pet_nome} ({obj.get_especie_display()})'

    @admin.display(description='Alerta', boolean=True)
    def alerta(self, obj):
        return obj.sinal_de_alerta

    @admin.display(description='WhatsApp')
    def whatsapp(self, obj):
        return format_html('<a href="{}" target="_blank" style="color:#16a34a;font-weight:600">Confirmar</a>',
                           _link_whatsapp(obj, _msg_confirmacao(obj)))

    @admin.display(description='Falar com o tutor')
    def botoes_whatsapp(self, obj):
        if not obj.pk:
            return '—'
        return format_html(
            '<a href="{}" target="_blank" style="display:inline-block;background:#16a34a;color:#fff;padding:6px 14px;'
            'border-radius:999px;font-weight:600;margin-right:8px">Confirmar pelo WhatsApp</a>'
            '<a href="{}" target="_blank" style="display:inline-block;border:1px solid #d1d5db;padding:6px 14px;'
            'border-radius:999px;font-weight:600">Pedir para remarcar</a>',
            _link_whatsapp(obj, _msg_confirmacao(obj)), _link_whatsapp(obj, _msg_remarcar(obj)))

    def _mudar(self, request, qs, status, texto):
        n = qs.update(status=status)
        self.message_user(request, f'{n} agendamento(s) marcado(s) como {texto}.', messages.SUCCESS)

    @admin.action(description='Marcar como confirmado')
    def marcar_confirmado(self, request, qs):
        self._mudar(request, qs, Agendamento.CONFIRMADO, 'confirmado')

    @admin.action(description='Marcar como atendido')
    def marcar_atendido(self, request, qs):
        self._mudar(request, qs, Agendamento.ATENDIDO, 'atendido')

    @admin.action(description='Marcar como cancelado (libera o horário)')
    def marcar_cancelado(self, request, qs):
        self._mudar(request, qs, Agendamento.CANCELADO, 'cancelado')


@admin.register(TipoAtendimento)
class TipoAtendimentoAdmin(ModelAdmin):
    list_display = ('nome', 'duracao', 'ordem', 'ativo')
    list_editable = ('duracao', 'ordem', 'ativo')


@admin.register(HorarioFuncionamento)
class HorarioFuncionamentoAdmin(ModelAdmin):
    list_display = ('dia_semana', 'abre', 'fecha', 'ativo')
    list_editable = ('abre', 'fecha', 'ativo')


@admin.register(Bloqueio)
class BloqueioAdmin(ModelAdmin):
    list_display = ('data', 'motivo')
