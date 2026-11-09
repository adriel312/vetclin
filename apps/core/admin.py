from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import ClinicaConfig, Membro


@admin.register(ClinicaConfig)
class ClinicaConfigAdmin(ModelAdmin):
    # Impede criação de mais de um registro
    def has_add_permission(self, request):
        return not ClinicaConfig.objects.exists()

    fieldsets = (
        ('Identidade', {'fields': ('nome', 'slogan', 'logo', 'imagem_topo', 'sobre')}),
        ('Contato',    {'fields': ('telefone', 'whatsapp', 'email')}),
        ('Endereço',   {'fields': ('endereco', 'bairro', 'cidade', 'estado', 'cep', 'google_maps_embed')}),
        ('Horários',   {'fields': ('horario_semana', 'horario_sabado', 'horario_domingo')}),
        ('Redes sociais', {'fields': ('instagram', 'facebook', 'youtube')}),
    )


@admin.register(Membro)
class MembroAdmin(ModelAdmin):
    list_display = ('nome', 'cargo', 'crmv', 'ordem', 'ativo')
    list_editable = ('ordem', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome', 'cargo')
