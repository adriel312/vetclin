from django.db import models


class ClinicaConfig(models.Model):
    """
    Singleton — configurações globais da clínica.
    Apenas um registro deve existir (garantido no admin).
    """
    nome = models.CharField('Nome da clínica', max_length=100)
    slogan = models.CharField('Slogan', max_length=200, blank=True)
    sobre = models.TextField('Sobre a clínica')
    logo = models.ImageField('Logo', upload_to='clinica/', blank=True, null=True)

    # Contato
    telefone = models.CharField('Telefone', max_length=20)
    whatsapp = models.CharField('WhatsApp', max_length=20)
    email = models.EmailField('E-mail')

    # Endereço
    endereco = models.CharField('Endereço', max_length=200)
    bairro = models.CharField('Bairro', max_length=100)
    cidade = models.CharField('Cidade', max_length=100)
    estado = models.CharField('Estado', max_length=2)
    cep = models.CharField('CEP', max_length=9)
    google_maps_embed = models.TextField('Embed do Google Maps', blank=True)

    # Horários
    horario_semana = models.CharField('Horário (seg–sex)', max_length=50, default='08:00 às 18:00')
    horario_sabado = models.CharField('Horário (sábado)', max_length=50, default='08:00 às 12:00')
    horario_domingo = models.CharField('Horário (domingo)', max_length=50, blank=True)

    # Redes sociais
    instagram = models.URLField('Instagram', blank=True)
    facebook = models.URLField('Facebook', blank=True)
    youtube = models.URLField('YouTube', blank=True)

    class Meta:
        verbose_name = 'Configuração da Clínica'
        verbose_name_plural = 'Configurações da Clínica'

    def __str__(self):
        return self.nome


class Membro(models.Model):
    """Médicos e funcionários exibidos na página Sobre."""
    nome = models.CharField('Nome', max_length=100)
    cargo = models.CharField('Cargo / Especialidade', max_length=100)
    crmv = models.CharField('CRMV', max_length=20, blank=True)
    bio = models.TextField('Bio curta', blank=True)
    foto = models.ImageField('Foto', upload_to='equipe/')
    ordem = models.PositiveSmallIntegerField('Ordem de exibição', default=0)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Membro da Equipe'
        verbose_name_plural = 'Equipe'
        ordering = ['ordem', 'nome']

    def __str__(self):
        return f'{self.nome} — {self.cargo}'
