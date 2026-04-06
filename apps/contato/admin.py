from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Mensagem


@admin.register(Mensagem)
class MensagemAdmin(ModelAdmin):
    list_display = ('nome', 'email', 'assunto', 'lida', 'criado_em')
    list_editable = ('lida',)
    list_filter = ('lida',)
    search_fields = ('nome', 'email', 'assunto')
    readonly_fields = ('nome', 'email', 'telefone', 'assunto', 'mensagem', 'criado_em')

    def has_add_permission(self, request):
        return False  # mensagens só chegam pelo formulário do site
