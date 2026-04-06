from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Categoria, Produto


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
