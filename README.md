# Clínica Veterinária — Sistema Web

Sistema web completo para clínica veterinária desenvolvido com **Django 5 + Tailwind CSS + HTMX**.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Django 5.0 (Python) |
| Admin | Django Admin + Unfold |
| Frontend | Tailwind CSS + HTMX + Alpine.js |
| Banco de dados | PostgreSQL |
| Imagens | Disco local do VPS (Cloudinary opcional) |
| Deploy | VPS Hostinger — Nginx + Gunicorn (ver DEPLOY_HOSTINGER.md) |

---

## Instalação local

```bash
# 1. Clone o repositório
git clone <url-do-repo>
cd clinica_vet

# 2. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais

# 5. Crie o banco de dados
createdb clinica_vet           # PostgreSQL

# 6. Rode as migrations
python manage.py migrate

# 7. Crie o superusuário (acesso ao admin)
python manage.py createsuperuser

# 8. Rode o servidor
python manage.py runserver
```

Acesse:
- **Site público:** http://localhost:8000
- **Painel admin:** http://localhost:8000/admin

---

## Estrutura do projeto

```
clinica_vet/
├── config/              # Configurações Django
│   ├── settings.py
│   └── urls.py
├── apps/
│   ├── core/            # Configurações da clínica + equipe + home
│   ├── produtos/        # Loja — produtos e categorias
│   ├── servicos/        # Serviços prestados
│   ├── exames/          # Exames e preços
│   └── contato/         # Formulário de contato
├── templates/
│   ├── base/            # base.html (layout principal)
│   ├── components/      # navbar, footer, whatsapp_btn
│   └── pages/           # home, produtos, servicos, exames, contato
├── static/              # CSS, JS, imagens
└── media/               # Upload de imagens (dev)
```

---

## Páginas disponíveis

| URL | Descrição |
|---|---|
| `/` | Home com destaques |
| `/servicos/` | Listagem de serviços |
| `/servicos/<slug>/` | Detalhe do serviço |
| `/exames/` | Tabela de exames e preços |
| `/produtos/` | Loja (com filtro por categoria) |
| `/produtos/<slug>/` | Detalhe do produto |
| `/contato/` | Formulário de contato |
| `/sobre/` | Sobre a clínica e equipe |
| `/admin/` | Painel administrativo |

---

## Painel administrativo (Unfold)

O administrador pode editar pelo painel:
- Informações da clínica (nome, endereço, horários, redes sociais)
- Equipe (médicos e funcionários)
- Produtos e categorias
- Serviços
- Exames e grupos de exames
- Mensagens recebidas via formulário

---

## Deploy

O projeto roda num VPS da Hostinger com Nginx + Gunicorn + PostgreSQL.
O passo a passo completo está em [DEPLOY_HOSTINGER.md](DEPLOY_HOSTINGER.md).

Para publicar uma atualização depois do `git push`:

```bash
sudo bash /srv/clinica_vet/deploy/atualizar.sh
```
