from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Servico


@admin.register(Servico)
class ServicoAdmin(ModelAdmin):
    list_display = ('nome', 'preco_a_partir', 'destaque', 'ativo', 'ordem')
    list_editable = ('destaque', 'ativo', 'ordem')
    prepopulated_fields = {'slug': ('nome',)}
