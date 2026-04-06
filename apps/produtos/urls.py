from django.urls import path
from . import views

app_name = 'produtos'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('<slug:slug>/', views.detalhe, name='detalhe'),
]
