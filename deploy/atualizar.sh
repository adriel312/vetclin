#!/usr/bin/env bash
# Atualiza o site após um "git push". Rodar no VPS como root:
#   sudo bash /srv/clinica_vet/deploy/atualizar.sh
set -euo pipefail

APP_DIR=/srv/clinica_vet
APP_USER=clinica

echo ">> Baixando código novo"
sudo -u "$APP_USER" git -C "$APP_DIR" pull --ff-only

echo ">> Dependências"
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/pip" install -q -r "$APP_DIR/requirements.txt"

echo ">> Migrations"
sudo -u "$APP_USER" bash -c "cd $APP_DIR && .venv/bin/python manage.py migrate --noinput"

echo ">> Arquivos estáticos"
sudo -u "$APP_USER" bash -c "cd $APP_DIR && .venv/bin/python manage.py collectstatic --noinput"

echo ">> Reiniciando Gunicorn"
systemctl restart gunicorn-clinica
systemctl --no-pager --lines=5 status gunicorn-clinica

echo ">> Pronto!"
