from django.contrib import admin
from django.contrib.admin import TabularInline
from unfold.admin import ModelAdmin
from .models import Campanha, Categoria, ItemCampanha, Produto


@admin.register(Categoria)
class CategoriaAdmin(ModelAdmin):
    list_display = ('nome', 'slug', 'ordem')
    list_editable = ('ordem',)
    prepopulated_fields = {'slug': ('nome',)}


@admin.register(Produto)
class ProdutoAdmin(ModelAdmin):
    list_display = ('nome', 'categoria', 'preco', 'destaque', 'ativo')
    list_editable = ('destaque', 'ativo')
    list_filter = ('categoria', 'destaque', 'ativo')
    search_fields = ('nome', 'marca')
    prepopulated_fields = {'slug': ('nome',)}
    fieldsets = (
        ('Informações', {'fields': ('nome', 'slug', 'categoria', 'marca', 'descricao')}),
        ('Preço e imagem', {'fields': ('preco', 'imagem')}),
        ('Configurações', {'fields': ('destaque', 'ativo')}),
    )


class ItemCampanhaInline(TabularInline):
    model = ItemCampanha
    extra = 3
    autocomplete_fields = ('produto',)
    fields = ('produto', 'desconto')


@admin.register(Campanha)
class CampanhaAdmin(ModelAdmin):
    list_display = ('nome', 'inicio', 'fim', 'desconto_padrao', 'toda_loja', 'ativo')
    list_editable = ('ativo',)
    fieldsets = (
        ('Campanha', {'fields': ('nome', 'frase_faixa', 'ativo')}),
        ('Período', {'fields': ('inicio', 'fim'),
                     'description': 'Fora deste período o site volta sozinho ao visual normal.'}),
        ('Desconto', {'fields': ('desconto_padrao', 'toda_loja')}),
    )
    inlines = [ItemCampanhaInline]
