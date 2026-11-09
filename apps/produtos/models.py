from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.text import slugify


class Categoria(models.Model):
    nome = models.CharField('Nome', max_length=80)
    slug = models.SlugField(unique=True, blank=True)
    icone = models.CharField('Ícone (Material Icons)', max_length=50, blank=True)
    ordem = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)


class Produto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='produtos')
    nome = models.CharField('Nome', max_length=150)
    slug = models.SlugField(unique=True, blank=True)
    descricao = models.TextField('Descrição', blank=True)
    preco = models.DecimalField('Preço (R$)', max_digits=10, decimal_places=2, null=True, blank=True)
    imagem = models.ImageField('Imagem', upload_to='produtos/')
    marca = models.CharField('Marca', max_length=80, blank=True)
    destaque = models.BooleanField('Destaque na home', default=False)
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['-destaque', 'nome']

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)


class Campanha(models.Model):
    """Promoção com data de início e fim (ex.: Black Friday).
    Fora do período, o site volta sozinho ao visual normal."""
    nome = models.CharField('Nome', max_length=60, default='Black Friday')
    frase_faixa = models.CharField('Texto da faixa no topo do site', max_length=120,
                                   default='Ofertas especiais na loja da clínica')
    inicio = models.DateTimeField('Começa em')
    fim = models.DateTimeField('Termina em')
    desconto_padrao = models.PositiveSmallIntegerField(
        'Desconto padrão (%)', default=15,
        help_text='Usado nos produtos da campanha que não tiverem um desconto próprio.')
    toda_loja = models.BooleanField(
        'Aplicar em toda a loja', default=False,
        help_text='Marcado: todos os produtos com preço recebem o desconto padrão. '
                  'Desmarcado: só os produtos listados abaixo entram na promoção.')
    ativo = models.BooleanField('Ativa', default=True,
                                help_text='Desmarque para encerrar a campanha antes da data.')

    class Meta:
        verbose_name = 'Campanha'
        verbose_name_plural = 'Campanhas (Black Friday etc.)'
        ordering = ['-inicio']

    def __str__(self):
        return self.nome

    @classmethod
    def atual(cls):
        agora = timezone.now()
        return cls.objects.filter(ativo=True, inicio__lte=agora, fim__gte=agora).first()

    @cached_property
    def _descontos(self):
        return {i.produto_id: (i.desconto or self.desconto_padrao) for i in self.itens.all()}

    def desconto_de(self, produto):
        """Percentual de desconto do produto nesta campanha, ou None."""
        if not produto.preco:
            return None
        if produto.pk in self._descontos:
            return self._descontos[produto.pk]
        return self.desconto_padrao if self.toda_loja else None

    @property
    def maior_desconto(self):
        valores = list(self._descontos.values())
        if self.toda_loja:
            valores.append(self.desconto_padrao)
        return max(valores, default=self.desconto_padrao)

    def oferta(self, produto):
        pct = self.desconto_de(produto)
        if not pct:
            return None
        final = (produto.preco * (100 - pct) / Decimal(100)).quantize(Decimal('0.01'), ROUND_HALF_UP)
        return {'pct': pct, 'de': produto.preco, 'por': final, 'economia': produto.preco - final}


class ItemCampanha(models.Model):
    campanha = models.ForeignKey(Campanha, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, verbose_name='Produto')
    desconto = models.PositiveSmallIntegerField('Desconto (%)', null=True, blank=True,
                                                help_text='Deixe vazio para usar o desconto padrão.')

    class Meta:
        verbose_name = 'Produto em oferta'
        verbose_name_plural = 'Produtos em oferta'
        unique_together = [('campanha', 'produto')]

    def __str__(self):
        return str(self.produto)
