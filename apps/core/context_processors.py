from .models import ClinicaConfig


def clinica_config(request):
    """Injeta as configurações da clínica em todos os templates."""
    try:
        config = ClinicaConfig.objects.first()
    except Exception:
        config = None
    return {'clinica': config}
