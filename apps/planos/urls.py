from django.urls import path
from . import views

app_name = 'planos'

urlpatterns = [
    path('', views.lista, name='lista'),
]
