from django.urls import path
from . import views

app_name = 'agenda'

urlpatterns = [
    path('', views.agendar, name='agendar'),
    path('horarios/', views.horarios, name='horarios'),
    path('pedido/<uuid:codigo>/', views.pedido, name='pedido'),
]
