from django.db import models


class Mensagem(models.Model):
    nome = models.CharField('Nome', max_length=100)
    email = models.EmailField('E-mail')
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    assunto = models.CharField('Assunto', max_length=150)
    mensagem = models.TextField('Mensagem')
    lida = models.BooleanField('Lida', default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mensagem'
        verbose_name_plural = 'Mensagens'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.nome} — {self.assunto}'
