from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.text import slugify


class PaginaPlano(models.Model):
    """Conteúdo geral da página do plano (registro único)."""
    video = models.FileField('Vídeo de apresentação', upload_to='plano/', blank=True,
                             validators=[FileExtensionValidator(['mp4', 'webm'])],
                             help_text='Arquivo .mp4 ou .webm. Aparece logo abaixo do topo da página.')
    video_capa = models.ImageField('Capa do vídeo (opcional)', upload_to='plano/', blank=True,
                                   help_text='Imagem mostrada enquanto o vídeo carrega.')
    video_titulo = models.CharField('Título ao lado do vídeo', max_length=120,
                                    default='Entenda o Clube Preventivo em poucos segundos')
    video_texto = models.TextField('Texto ao lado do vídeo', blank=True,
                                   default='Veja como funciona o plano e como ele ajuda a cuidar do seu pet o ano todo, '
                                           'gastando menos com consultas, exames e vacinas.')
    observacao = models.TextField('Observação abaixo dos planos', blank=True,
                                  default='* Os descontos em cirurgias aplicam-se exclusivamente a procedimentos eletivos '
                                          'e de baixa complexidade. Cirurgias de maior complexidade serão avaliadas '
                                          'individualmente.')

    class Meta:
        verbose_name = 'Página do plano'
        verbose_name_plural = 'Página do plano'

    def __str__(self):
        return 'Página do plano'


class Plano(models.Model):
    """Planos do Clube Preventivo (plano de saúde pet)."""
    nome = models.CharField('Nome do plano', max_length=80)
    slug = models.SlugField(unique=True, blank=True)
    subtitulo = models.CharField('Frase curta', max_length=150, blank=True,
                                 help_text='Ex.: "Cuidado preventivo para o dia a dia".')
    preco_mensal = models.DecimalField('Mensalidade (R$)', max_digits=8, decimal_places=2)
    valor_avulso = models.DecimalField('Quanto custaria tudo avulso por ano (R$)', max_digits=10, decimal_places=2,
                                       null=True, blank=True,
                                       help_text='Opcional. Se preencher, a página mostra quanto o cliente economiza.')
    destaque = models.BooleanField('Destacar como "recomendado"', default=False)
    ordem = models.PositiveSmallIntegerField('Ordem de exibição', default=0)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Plano'
        verbose_name_plural = 'Planos'
        ordering = ['ordem', 'preco_mensal']

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    @property
    def economia_anual(self):
        anual = self.preco_mensal * 12
        if self.valor_avulso and self.valor_avulso > anual:
            return self.valor_avulso - anual
        return None

    def _grupo(self, grupo):
        return [b for b in self.beneficios.all() if b.grupo == grupo]

    @property
    def inclusos(self):
        return self._grupo(Beneficio.INCLUSO)

    @property
    def descontos(self):
        return self._grupo(Beneficio.DESCONTO)

    @property
    def adicionais(self):
        return self._grupo(Beneficio.ADICIONAL)


class Beneficio(models.Model):
    """Um item do plano: algo incluso, um desconto ou um benefício adicional."""
    INCLUSO, DESCONTO, ADICIONAL = 'incluso', 'desconto', 'adicional'
    GRUPOS = [
        (INCLUSO, 'Incluso no plano'),
        (DESCONTO, 'Desconto'),
        (ADICIONAL, 'Benefício adicional'),
    ]
    plano = models.ForeignKey(Plano, on_delete=models.CASCADE, related_name='beneficios')
    grupo = models.CharField('Tipo', max_length=10, choices=GRUPOS, default=INCLUSO)
    texto = models.CharField('Texto', max_length=150)
    valor = models.CharField('Valor do desconto', max_length=20, blank=True,
                             help_text='Só para descontos. Ex.: "20%".')
    ordem = models.PositiveSmallIntegerField('Ordem', default=0)

    class Meta:
        verbose_name = 'Item do plano'
        verbose_name_plural = 'Itens do plano'
        ordering = ['ordem', 'id']

    def __str__(self):
        return self.texto


class PerguntaFrequente(models.Model):
    pergunta = models.CharField('Pergunta', max_length=200)
    resposta = models.TextField('Resposta')
    ordem = models.PositiveSmallIntegerField('Ordem', default=0)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Pergunta frequente'
        verbose_name_plural = 'Perguntas frequentes'
        ordering = ['ordem', 'id']

    def __str__(self):
        return self.pergunta
