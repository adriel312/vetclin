from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContatoForm


def contato(request):
    form = ContatoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        msg = form.save()
        # Envia e-mail de notificação para a clínica
        send_mail(
            subject=f'[Site] {msg.assunto}',
            message=f'De: {msg.nome} <{msg.email}>\nTelefone: {msg.telefone}\n\n{msg.mensagem}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=True,
        )
        messages.success(request, 'Mensagem enviada com sucesso! Entraremos em contato em breve.')
        return redirect('contato:contato')
    return render(request, 'pages/contato.html', {'form': form})
