import re

from django.contrib import admin, messages
from django.contrib.admin import TabularInline
from unfold.admin import ModelAdmin
from .models import Campanha, Categoria, ItemCampanha, Produto, Tamanho


@admin.register(Categoria)
class CategoriaAdmin(ModelAdmin):
    list_display = ('nome', 'slug', 'ordem')
    list_editable = ('ordem',)
    prepopulated_fields = {'slug': ('nome',)}


# Acha o peso/volume no nome: "Ração Golden 10,1 kg" → "10,1 kg"
TAMANHO_NO_NOME = re.compile(r'\b(\d+(?:[.,]\d+)?\s?(?:kg|g|mg|ml|l|un|unidades?))\b', re.IGNORECASE)


class TamanhoInline(TabularInline):
    model = Tamanho
    extra = 2
    fields = ('nome', 'preco', 'ordem', 'ativo')
    verbose_name = 'Tamanho'
    verbose_name_plural = 'Tamanhos (ex.: ração de 1 kg, 3 kg, 10 kg). Deixe vazio se o produto tiver um preço só.'


@admin.register(Produto)
class ProdutoAdmin(ModelAdmin):
    list_display = ('nome', 'categoria', 'preco', 'qtd_tamanhos', 'destaque', 'ativo')
    list_editable = ('destaque', 'ativo')
    list_filter = ('categoria', 'destaque', 'ativo')
    search_fields = ('nome', 'marca')
    prepopulated_fields = {'slug': ('nome',)}
    fieldsets = (
        ('Informações', {'fields': ('nome', 'slug', 'categoria', 'marca', 'descricao')}),
        ('Preço e imagem', {'fields': ('preco', 'imagem'),
                            'description': 'Se cadastrar tamanhos abaixo, o preço é preenchido sozinho com o do menor tamanho.'}),
        ('Configurações', {'fields': ('destaque', 'ativo')}),
    )
    inlines = [TamanhoInline]
    actions = ['juntar_como_tamanhos']

    @admin.display(description='Tamanhos')
    def qtd_tamanhos(self, obj):
        n = obj.tamanhos.filter(ativo=True).count()
        return n or '—'

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.sincronizar_preco()

    @admin.action(description='Juntar os produtos selecionados em um só, com opção de tamanho')
    def juntar_como_tamanhos(self, request, queryset):
        produtos = list(queryset.order_by('preco', 'nome'))
        if len(produtos) < 2:
            self.message_user(request, 'Selecione pelo menos 2 produtos (ex.: a mesma ração de 1 kg, 3 kg e 10 kg).',
                              messages.WARNING)
            return
        sem_preco = [p.nome for p in produtos if not p.preco]
        if sem_preco:
            self.message_user(request, 'Estes produtos estão sem preço: ' + ', '.join(sem_preco), messages.ERROR)
            return

        base = produtos[0]
        ordem = base.tamanhos.count()
        for p in produtos:
            achado = TAMANHO_NO_NOME.search(p.nome)
            nome_tamanho = achado.group(1) if achado else p.nome[:30]
            Tamanho.objects.create(produto=base, nome=nome_tamanho, preco=p.preco, ordem=ordem)
            ordem += 1
            if p.pk != base.pk:
                # Se a versão antiga estava numa campanha, a nova também entra
                for item in ItemCampanha.objects.filter(produto=p):
                    ItemCampanha.objects.get_or_create(campanha=item.campanha, produto=base,
                                                       defaults={'desconto': item.desconto})
                if p.destaque:
                    base.destaque = True
                p.ativo = False
                p.save(update_fields=['ativo'])

        achado = TAMANHO_NO_NOME.search(base.nome)
        if achado:
            base.nome = re.sub(r'\s{2,}', ' ', base.nome.replace(achado.group(1), '')).strip(' -–')
        base.save()
        base.sincronizar_preco()
        self.message_user(
            request,
            f'Pronto! "{base.nome}" agora tem {len(produtos)} tamanhos. Os outros produtos foram desativados '
            f'(não apagados). Confira os nomes dos tamanhos abrindo o produto.',
            messages.SUCCESS)


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
