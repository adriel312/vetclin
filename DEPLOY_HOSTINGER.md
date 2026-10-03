# Deploy na Hostinger VPS (KVM 2) — Nginx + Gunicorn + PostgreSQL

Arquitetura final:

```
Navegador ──HTTPS──> Nginx (porta 80/443)
                       ├── /static/  → /srv/clinica_vet/staticfiles/
                       ├── /media/   → /srv/clinica_vet/media/
                       └── /         → Gunicorn (socket) → Django → PostgreSQL (local)
```

Nos comandos abaixo, troque sempre:

- `seudominio.com.br` → seu domínio real
- `IP_DO_VPS` → IP do seu VPS (hPanel → VPS → Visão geral)

Considera-se um VPS com **Ubuntu 22.04 ou 24.04** sem painel (CloudPanel, Coolify etc.).

---

## Passo 0 — No seu computador (Windows)

Substitua os arquivos do projeto pelos desta versão, depois envie para o GitHub:

```powershell
git add -A
git commit -m "Prepara projeto para deploy na Hostinger VPS"
git push origin main
```

> O `.env` e a pasta `media/` NÃO vão para o GitHub (estão no `.gitignore`). Isso é correto: eles serão enviados ao servidor separadamente (passo 13).

---

## Passo 1 — Apontar o domínio para o VPS

No hPanel → **Domínios → seu domínio → DNS / Nameservers**, crie (ou edite) os registros:

| Tipo | Nome | Aponta para | TTL |
|------|------|-------------|-----|
| A    | @    | IP_DO_VPS   | 300 |
| A    | www  | IP_DO_VPS   | 300 |

Apague registros A/AAAA/CNAME antigos de `@` e `www` que apontem para outro lugar. A propagação leva de minutos a algumas horas — por isso é o primeiro passo.

Se o domínio estiver em outro registrador (Registro.br, GoDaddy…), crie os mesmos registros lá.

---

## Passo 2 — Entrar no VPS e fazer o diagnóstico

```bash
ssh root@IP_DO_VPS
```

```bash
lsb_release -a                              # versão do Ubuntu
sudo ss -tlnp | grep -E ':80 |:443 '        # quem está usando as portas web
```

- Nenhuma saída no segundo comando, ou só `nginx` → siga o guia normalmente.
- Aparece `apache2`, `docker-proxy`, `traefik`, `caddy`, `coolify` ou outro → **pare aqui**: já existe outro serviço ocupando as portas e o passo 11 precisa ser adaptado.

---

## Passo 3 — Atualizar o sistema e instalar os pacotes

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git nginx \
    postgresql postgresql-contrib certbot python3-certbot-nginx
```

---

## Passo 4 — Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable          # responda "y"
sudo ufw status
```

Se você ativou o firewall do próprio hPanel (VPS → Segurança → Firewall), libere lá também as portas **22, 80 e 443**.

---

## Passo 5 — Criar o banco PostgreSQL

Gere uma senha forte e anote-a (será usada no `.env`):

```bash
openssl rand -base64 24
```

```bash
sudo -u postgres psql
```

Dentro do `psql` (troque a senha):

```sql
CREATE USER clinica_user WITH PASSWORD 'COLE_A_SENHA_AQUI';
CREATE DATABASE clinica_vet OWNER clinica_user ENCODING 'UTF8';
ALTER ROLE clinica_user SET client_encoding TO 'utf8';
ALTER ROLE clinica_user SET timezone TO 'America/Sao_Paulo';
\q
```

---

## Passo 6 — Usuário do sistema e código

O site roda com um usuário próprio (`clinica`), nunca como root.

```bash
sudo adduser --system --group --home /srv/clinica_vet --shell /bin/bash clinica
sudo usermod -aG www-data clinica
sudo chown clinica:www-data /srv/clinica_vet
sudo chmod 2750 /srv/clinica_vet
```

Clonar o repositório:

```bash
sudo -u clinica git clone https://github.com/adriel312/vetclin.git /srv/clinica_vet
```

> **Repositório privado?** O Git vai pedir usuário e senha. A senha NÃO é a do GitHub: crie um token em GitHub → Settings → Developer settings → Personal access tokens → Fine-grained → acesso de leitura (*Contents: Read*) só ao repositório `vetclin`, e cole o token no lugar da senha. Para não precisar digitar de novo nas próximas atualizações:
> `sudo -u clinica git -C /srv/clinica_vet config credential.helper store` (antes do primeiro `pull`).

---

## Passo 7 — Ambiente virtual e dependências

```bash
cd /srv/clinica_vet
sudo -u clinica python3 -m venv .venv
sudo -u clinica .venv/bin/pip install --upgrade pip
sudo -u clinica .venv/bin/pip install -r requirements.txt
sudo -u clinica mkdir -p media
```

---

## Passo 8 — Arquivo `.env` de produção

Gere a `SECRET_KEY`:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

Crie o arquivo:

```bash
sudo -u clinica cp .env.example .env
sudo -u clinica nano .env
```

Preencha (os principais):

```env
SECRET_KEY=a-chave-gerada-acima
DEBUG=False
ALLOWED_HOSTS=seudominio.com.br,www.seudominio.com.br,IP_DO_VPS
CSRF_TRUSTED_ORIGINS=https://seudominio.com.br,https://www.seudominio.com.br
HTTPS_ENABLED=False

DB_NAME=clinica_vet
DB_USER=clinica_user
DB_PASSWORD=a-senha-do-passo-5
DB_HOST=localhost
DB_PORT=5432

USE_CLOUDINARY=False
```

Complete também WhatsApp e e-mail. Salve com `Ctrl+O`, `Enter`, `Ctrl+X`, e proteja o arquivo:

```bash
sudo chmod 600 /srv/clinica_vet/.env
```

---

## Passo 9 — Banco, arquivos estáticos e checagem

```bash
cd /srv/clinica_vet
sudo -u clinica .venv/bin/python manage.py migrate
sudo -u clinica .venv/bin/python manage.py collectstatic --noinput
sudo -u clinica .venv/bin/python manage.py check --deploy
```

O `check --deploy` pode mostrar avisos de HSTS/SSL — é normal neste momento. **Erros** (`ERRORS:`) não são.

Se você **não** for trazer os dados do seu computador (passo 13), crie o administrador agora:

```bash
sudo -u clinica .venv/bin/python manage.py createsuperuser
```

---

## Passo 10 — Gunicorn como serviço (systemd)

```bash
sudo cp /srv/clinica_vet/deploy/gunicorn-clinica.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn-clinica
sudo systemctl status gunicorn-clinica        # deve mostrar "active (running)"
```

Teste direto no socket (deve responder `HTTP/1.1 200 OK`):

```bash
curl -sI --unix-socket /run/clinica_vet/gunicorn.sock http://localhost/ -H "Host: IP_DO_VPS"
```

---

## Passo 11 — Nginx

```bash
sudo cp /srv/clinica_vet/deploy/nginx-clinica.conf /etc/nginx/sites-available/clinica
sudo sed -i 's/seudominio.com.br/SEUDOMINIO_REAL.com.br/g' /etc/nginx/sites-available/clinica
sudo ln -s /etc/nginx/sites-available/clinica /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t                                  # deve dizer "syntax is ok" e "test is successful"
sudo systemctl reload nginx
```

> Só remova o `default` se ele não estiver servindo outro site seu.

Acesse `http://seudominio.com.br` — o site já deve abrir (ainda sem cadeado).

---

## Passo 12 — HTTPS (certificado gratuito Let's Encrypt)

Só funciona depois que o DNS do passo 1 propagou (`ping seudominio.com.br` precisa responder com o IP do VPS).

```bash
sudo certbot --nginx -d seudominio.com.br -d www.seudominio.com.br \
    --redirect --agree-tos -m seu-email@exemplo.com
```

Depois, ative os cookies seguros no `.env`:

```bash
sudo -u clinica sed -i 's/^HTTPS_ENABLED=.*/HTTPS_ENABLED=True/' /srv/clinica_vet/.env
sudo systemctl restart gunicorn-clinica
```

A renovação é automática. Para conferir: `sudo certbot renew --dry-run`.

Acesse `https://seudominio.com.br/admin` e faça login.

---

## Passo 13 — (Opcional) Levar dados e imagens do seu computador

Faça isto se você já cadastrou produtos, serviços, configurações da clínica etc. no ambiente local e quer os mesmos dados no site.

**No Windows**, na pasta do projeto, com o venv ativado:

```powershell
python -X utf8 manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission -e admin.logentry -e sessions --indent 2 -o dados.json
scp dados.json root@IP_DO_VPS:/tmp/
scp -r media root@IP_DO_VPS:/tmp/
```

**No VPS:**

```bash
cd /srv/clinica_vet
sudo cp -r /tmp/media/. /srv/clinica_vet/media/
sudo chown -R clinica:www-data /srv/clinica_vet/media
sudo -u clinica .venv/bin/python manage.py loaddata /tmp/dados.json
sudo rm -rf /tmp/dados.json /tmp/media
sudo systemctl restart gunicorn-clinica
```

O `dados.json` inclui os usuários locais, então você entra no admin com o mesmo login do seu computador. Rode o `loaddata` num banco recém-migrado e ainda vazio (sem ter feito `createsuperuser` antes), para não dar conflito.

---

## Atualizações futuras

No computador: `git add -A`, `git commit`, `git push`. No VPS:

```bash
sudo bash /srv/clinica_vet/deploy/atualizar.sh
```

O script faz `git pull`, instala dependências, roda migrations, `collectstatic` e reinicia o Gunicorn.

---

## Backup do banco (recomendado)

```bash
sudo mkdir -p /var/backups/clinica
sudo crontab -e
```

Adicione a linha (backup diário às 3h, mantém 14 dias):

```
0 3 * * * sudo -u postgres pg_dump -Fc clinica_vet > /var/backups/clinica/db_$(date +\%F).dump && find /var/backups/clinica -name "*.dump" -mtime +14 -delete
```

A pasta `/srv/clinica_vet/media` também deve entrar no seu backup. Os snapshots semanais do hPanel ajudam, mas não substituem isso.

---

## Problemas comuns

| Sintoma | Onde olhar / solução |
|---|---|
| **502 Bad Gateway** | Gunicorn caiu: `sudo journalctl -u gunicorn-clinica -n 50 --no-pager` |
| **400 Bad Request** | Domínio/IP faltando em `ALLOWED_HOSTS` no `.env` → reinicie o gunicorn |
| **403 CSRF no login do admin** | `CSRF_TRUSTED_ORIGINS` precisa ter `https://` e o domínio exato (com e sem `www`) |
| **Site sem CSS / admin quebrado** | Rodou `collectstatic`? Confira `ls /srv/clinica_vet/staticfiles` e `sudo tail /var/log/nginx/clinica_error.log` |
| **Imagens não aparecem (404)** | Arquivos em `/srv/clinica_vet/media`? Dono `clinica:www-data`? |
| **Imagens dão 403** | Permissão: `sudo chown -R clinica:www-data /srv/clinica_vet/media && sudo chmod -R g+rX /srv/clinica_vet/media` |
| **Erro 413 ao enviar imagem** | Aumente `client_max_body_size` no Nginx |
| **Alterei o `.env` e nada mudou** | `sudo systemctl restart gunicorn-clinica` |
| **Formulário de contato não envia e-mail** | Gmail exige "senha de app" (não a senha normal) em `EMAIL_HOST_PASSWORD` |

Logs úteis:

```bash
sudo journalctl -u gunicorn-clinica -f          # Django/Gunicorn ao vivo
sudo tail -f /var/log/nginx/clinica_error.log    # Nginx
```
