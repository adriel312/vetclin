from .models import Campanha


def campanha_ativa(request):
    """Disponibiliza a campanha em andamento (ou None) para todos os templates."""
    try:
        return {'campanha': Campanha.atual()}
    except Exception:
        return {'campanha': None}
