from django import forms
from .models import Mensagem


class ContatoForm(forms.ModelForm):
    class Meta:
        model = Mensagem
        fields = ('nome', 'email', 'telefone', 'assunto', 'mensagem')
        widgets = {
            'nome':     forms.TextInput(attrs={'placeholder': 'Seu nome'}),
            'email':    forms.EmailInput(attrs={'placeholder': 'seu@email.com'}),
            'telefone': forms.TextInput(attrs={'placeholder': '(11) 99999-9999'}),
            'assunto':  forms.TextInput(attrs={'placeholder': 'Como podemos ajudar?'}),
            'mensagem': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Sua mensagem...'}),
        }
