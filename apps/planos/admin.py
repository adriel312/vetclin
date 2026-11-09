from django.contrib import admin
from django.contrib.admin import TabularInline
from unfold.admin import ModelAdmin
from .models import PaginaPlano, Plano, Beneficio, PerguntaFrequente


@admin.register(PaginaPlano)
class PaginaPlanoAdmin(ModelAdmin):
    fieldsets = (
        ('Vídeo', {'fields': ('video', 'video_capa', 'video_titulo', 'video_texto')}),
        ('Planos', {'fields': ('observacao',)}),
    )

    def has_add_permission(self, request):
        return not PaginaPlano.objects.exists()


class BeneficioInline(TabularInline):
    model = Beneficio
    extra = 3
    fields = ('grupo', 'texto', 'valor', 'ordem')


@admin.register(Plano)
class PlanoAdmin(ModelAdmin):
    list_display = ('nome', 'preco_mensal', 'destaque', 'ordem', 'ativo')
    list_editable = ('destaque', 'ordem', 'ativo')
    prepopulated_fields = {'slug': ('nome',)}
    inlines = [BeneficioInline]


@admin.register(PerguntaFrequente)
class PerguntaFrequenteAdmin(ModelAdmin):
    list_display = ('pergunta', 'ordem', 'ativo')
    list_editable = ('ordem', 'ativo')
