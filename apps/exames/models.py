from django.db import models


class GrupoExame(models.Model):
    nome = models.CharField('Grupo', max_length=80)
    ordem = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Grupo de Exame'
        verbose_name_plural = 'Grupos de Exame'
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome


class Exame(models.Model):
    grupo = models.ForeignKey(GrupoExame, on_delete=models.SET_NULL, null=True, blank=True, related_name='exames')
    nome = models.CharField('Nome do exame', max_length=150)
    descricao = models.TextField('Descrição / Preparo', blank=True)
    preco = models.DecimalField('Preço (R$)', max_digits=10, decimal_places=2, null=True, blank=True)
    prazo_resultado = models.CharField('Prazo do resultado', max_length=80, blank=True)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Exame'
        verbose_name_plural = 'Exames'
        ordering = ['grupo__ordem', 'nome']

    def __str__(self):
        return self.nome
