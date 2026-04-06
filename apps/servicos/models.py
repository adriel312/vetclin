from django.db import models
from django.utils.text import slugify


class Servico(models.Model):
    nome = models.CharField('Nome', max_length=150)
    slug = models.SlugField(unique=True, blank=True)
    descricao = models.TextField('Descrição')
    descricao_curta = models.CharField('Descrição curta (card)', max_length=160, blank=True)
    icone = models.CharField('Ícone (Material Icons)', max_length=50, blank=True)
    imagem = models.ImageField('Imagem', upload_to='servicos/', blank=True, null=True)
    preco_a_partir = models.DecimalField('A partir de (R$)', max_digits=10, decimal_places=2, null=True, blank=True)
    destaque = models.BooleanField('Destaque na home', default=False)
    ativo = models.BooleanField('Ativo', default=True)
    ordem = models.PositiveSmallIntegerField('Ordem', default=0)

    class Meta:
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços'
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)
