from django.contrib import admin
from unfold.admin import ModelAdmin
from django.contrib.admin import TabularInline
from .models import GrupoExame, Exame


class ExameInline(TabularInline):
    model = Exame
    extra = 1
    fields = ('nome', 'preco', 'prazo_resultado', 'ativo')


@admin.register(GrupoExame)
class GrupoExameAdmin(ModelAdmin):
    list_display = ('nome', 'ordem')
    list_editable = ('ordem',)
    inlines = [ExameInline]


@admin.register(Exame)
class ExameAdmin(ModelAdmin):
    list_display = ('nome', 'grupo', 'preco', 'prazo_resultado', 'ativo')
    list_editable = ('ativo',)
    list_filter = ('grupo', 'ativo')
    search_fields = ('nome',)
