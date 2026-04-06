from django.db import models
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
