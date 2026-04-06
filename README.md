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
| Imagens | Cloudinary |
| Deploy | Railway / Render |

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

## Deploy (Railway)

```bash
# Adicione ao requirements.txt:
gunicorn==22.0.0

# Procfile
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

No Railway, configure as variáveis de ambiente do `.env.example`.

---

## Futuro: Área de Associados

A estrutura já está preparada para adicionar o app `apps.associados` com:
- Modelo `Plano` (mensal/anual, cobertura)
- Modelo `Associado` (ligado ao User do Django)
- Login com área restrita
- Histórico de consultas e exames


---

## Deploy no Railway (passo a passo)

### 1. Pré-requisitos
- Conta no [Railway](https://railway.app)
- Conta no [Cloudinary](https://cloudinary.com) (gratuito)
- Repositório Git (GitHub recomendado)

### 2. Suba o código para o GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/seu-usuario/clinica-vet.git
git push -u origin main
```

### 3. Crie o projeto no Railway
1. Acesse railway.app → New Project → Deploy from GitHub Repo
2. Selecione o repositório
3. Railway detecta automaticamente o `Procfile` e o `nixpacks.toml`

### 4. Adicione o PostgreSQL
No painel Railway: **New Service → Database → PostgreSQL**

O Railway injeta automaticamente a variável `DATABASE_URL`. No `settings.py`, adapte para ler essa variável se preferir usar `dj-database-url`:
```bash
pip install dj-database-url
```
```python
import dj_database_url
DATABASES = {'default': dj_database_url.config(conn_max_age=600)}
```

### 5. Configure as variáveis de ambiente
No Railway, vá em **Variables** e adicione todas as variáveis do `.env.example`:
```
SECRET_KEY=gere-uma-chave-segura
DEBUG=False
ALLOWED_HOSTS=seu-dominio.railway.app
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
CONTACT_EMAIL=...
WHATSAPP_NUMBER=...
```

### 6. Gerar SECRET_KEY segura
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 7. Primeiro deploy
O Railway executa automaticamente (via `nixpacks.toml`):
- `pip install -r requirements.txt`
- `python manage.py collectstatic --noinput`
- `python manage.py migrate`

### 8. Criar superusuário em produção
No Railway, abra o terminal do serviço e rode:
```bash
python manage.py createsuperuser
```

### Domínio customizado
No Railway: **Settings → Domains → Custom Domain** → configure o DNS do seu provedor.

---

## Checklist de produção

- [ ] `DEBUG=False` no `.env`
- [ ] `SECRET_KEY` gerada e segura
- [ ] `ALLOWED_HOSTS` com o domínio real
- [ ] Cloudinary configurado
- [ ] E-mail SMTP configurado
- [ ] Superusuário criado
- [ ] Primeiro registro de `ClinicaConfig` criado no admin
- [ ] Migrações aplicadas

