import re

from django import forms

from .disponibilidade import esta_livre, proximos_dias
from .models import Agendamento, TipoAtendimento

SINTOMAS = [
    ('Sem sintomas (rotina / check-up)', 'Sem sintomas (rotina / check-up)'),
    ('Vômito', 'Vômito'),
    ('Diarreia', 'Diarreia'),
    ('Não está comendo', 'Não está comendo'),
    ('Quieto / sem energia', 'Quieto / sem energia'),
    ('Coceira ou feridas na pele', 'Coceira ou feridas na pele'),
    ('Mancando', 'Mancando'),
    ('Tosse ou espirros', 'Tosse ou espirros'),
    ('Olhos ou ouvidos', 'Problema nos olhos ou ouvidos'),
    ('Alteração no xixi', 'Alteração no xixi'),
]
# Sintomas que pedem atendimento imediato: o site mostra um aviso para ligar/chamar a clínica.
SINAIS_DE_ALERTA = [
    ('Convulsão', 'Convulsão'),
    ('Dificuldade para respirar', 'Dificuldade para respirar'),
    ('Sangramento intenso', 'Sangramento intenso'),
    ('Atropelamento ou queda', 'Atropelamento ou queda'),
    ('Suspeita de envenenamento', 'Suspeita de envenenamento'),
]


class AgendamentoForm(forms.Form):
    tipo = forms.ModelChoiceField(queryset=TipoAtendimento.objects.filter(ativo=True), empty_label=None,
                                  error_messages={'required': 'Escolha o tipo de atendimento.'})
    data = forms.DateField(error_messages={'required': 'Escolha o dia.'})
    hora = forms.TimeField(error_messages={'required': 'Escolha o horário.'})

    pet_nome = forms.CharField(max_length=60, error_messages={'required': 'Informe o nome do pet.'})
    especie = forms.ChoiceField(choices=Agendamento.ESPECIES, error_messages={'required': 'Informe se é cão, gato ou outro.'})
    raca = forms.CharField(max_length=60, required=False)
    idade = forms.CharField(max_length=30, required=False)
    peso = forms.CharField(max_length=20, required=False)
    primeira_vez = forms.BooleanField(required=False)

    sintomas = forms.MultipleChoiceField(choices=SINTOMAS + SINAIS_DE_ALERTA, required=False)
    descricao = forms.CharField(max_length=1500, required=False)

    tutor_nome = forms.CharField(max_length=100, error_messages={'required': 'Informe o seu nome.'})
    tutor_whatsapp = forms.CharField(max_length=20, error_messages={'required': 'Informe o seu WhatsApp.'})
    tutor_email = forms.EmailField(required=False, error_messages={'invalid': 'E-mail inválido.'})
    consentimento = forms.BooleanField(error_messages={
        'required': 'Para agendar, autorize o uso dos dados para contato sobre o atendimento.'})
    website = forms.CharField(required=False)  # campo escondido contra robôs

    def clean_tutor_whatsapp(self):
        digitos = re.sub(r'\D', '', self.cleaned_data['tutor_whatsapp'])
        if not 10 <= len(digitos) <= 13:
            raise forms.ValidationError('Informe o WhatsApp com DDD. Ex.: (63) 99999-9999')
        return self.cleaned_data['tutor_whatsapp'].strip()

    def clean(self):
        dados = super().clean()
        if dados.get('website'):
            raise forms.ValidationError('Não foi possível enviar. Tente novamente.')
        tipo, dia, hora = dados.get('tipo'), dados.get('data'), dados.get('hora')
        if tipo and dia and hora:
            if dia not in proximos_dias() or not esta_livre(tipo, dia, hora):
                self.add_error('hora', 'Esse horário acabou de ser ocupado. Escolha outro, por favor.')
        if not dados.get('sintomas') and not (dados.get('descricao') or '').strip():
            self.add_error('descricao', 'Conte rapidamente o motivo da visita ou marque um sintoma.')
        return dados

    @property
    def tem_alerta(self):
        alerta = {v for v, _ in SINAIS_DE_ALERTA}
        return any(s in alerta for s in self.cleaned_data.get('sintomas', []))
