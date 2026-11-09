"""
Configurações do projeto Clínica Veterinária
Preparado para rodar em desenvolvimento (DEBUG=True) e em produção
num VPS (Hostinger KVM) com Nginx + Gunicorn + PostgreSQL.
"""
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# Obrigatório no Django 4+ para o login do admin funcionar via HTTPS
# Ex.: https://meudominio.com.br,https://www.meudominio.com.br
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='', cast=Csv())

# Cloudinary é opcional. No VPS as imagens ficam no próprio disco (pasta media/).
USE_CLOUDINARY = config('USE_CLOUDINARY', default=False, cast=bool)

DJANGO_APPS = [
    'unfold',                        # django-unfold 1.0.0
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'crispy_forms',
    'crispy_tailwind',
    'django_extensions',
]

if USE_CLOUDINARY:
    THIRD_PARTY_APPS = ['cloudinary', 'cloudinary_storage'] + THIRD_PARTY_APPS

LOCAL_APPS = [
    'apps.core',
    'apps.produtos',
    'apps.servicos',
    'apps.exames',
    'apps.contato',
    'apps.planos',
    'apps.painel',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.clinica_config',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='clinica_vet'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': config('DB_CONN_MAX_AGE', default=60, cast=int),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# ─── Arquivos estáticos (CSS/JS/admin) ────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

# ─── Uploads (imagens de produtos, serviços, equipe, logo) ────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = Path(config('MEDIA_ROOT', default=str(BASE_DIR / 'media')))

# Django 5: STORAGES substitui DEFAULT_FILE_STORAGE / STATICFILES_STORAGE
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': (
            'django.contrib.staticfiles.storage.StaticFilesStorage'
            if DEBUG else
            'whitenoise.storage.CompressedManifestStaticFilesStorage'
        ),
    },
}

if USE_CLOUDINARY:
    STORAGES['default']['BACKEND'] = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default=''),
        'API_KEY':    config('CLOUDINARY_API_KEY', default=''),
        'API_SECRET': config('CLOUDINARY_API_SECRET', default=''),
    }

# Limite de upload (as imagens passam pelo Nginx, que também precisa permitir)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_PERMISSIONS = 0o644

# ─── E-mail ───────────────────────────────────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='')
CONTACT_EMAIL = config('CONTACT_EMAIL', default='')
SERVER_EMAIL = DEFAULT_FROM_EMAIL or 'root@localhost'

WHATSAPP_NUMBER = config('WHATSAPP_NUMBER', default='')
WHATSAPP_MESSAGE = config('WHATSAPP_MESSAGE', default='Ola! Gostaria de mais informacoes.')

CRISPY_ALLOWED_TEMPLATE_PACKS = 'tailwind'
CRISPY_TEMPLATE_PACK = 'tailwind'

UNFOLD = {
    'SITE_TITLE': 'Clinica Veterinaria - Admin',
    'SITE_HEADER': 'Painel Administrativo',
    'SITE_URL': '/',
    'SHOW_HISTORY': True,
    'SHOW_VIEW_ON_SITE': True,
    'SIDEBAR': {
        'show_search': True,
        'show_all_applications': True,
        'navigation': [
            {
                'title': 'Loja',
                'items': [
                    {'title': 'Produtos',   'icon': 'shopping_bag',    'link': '/admin/produtos/produto/'},
                    {'title': 'Categorias', 'icon': 'category',        'link': '/admin/produtos/categoria/'},
                ],
            },
            {
                'title': 'Plano de Saude',
                'items': [
                    {'title': 'Planos',     'icon': 'health_and_safety', 'link': '/admin/planos/plano/'},
                    {'title': 'Pagina e video', 'icon': 'movie',       'link': '/admin/planos/paginaplano/'},
                    {'title': 'Perguntas',  'icon': 'help',            'link': '/admin/planos/perguntafrequente/'},
                ],
            },
            {
                'title': 'Servicos e Exames',
                'items': [
                    {'title': 'Servicos',   'icon': 'medical_services','link': '/admin/servicos/servico/'},
                    {'title': 'Exames',     'icon': 'biotech',         'link': '/admin/exames/exame/'},
                ],
            },
            {
                'title': 'Clinica',
                'items': [
                    {'title': 'Configuracoes','icon': 'settings',      'link': '/admin/core/clinicaconfig/'},
                    {'title': 'Equipe',      'icon': 'group',          'link': '/admin/core/membro/'},
                    {'title': 'Contatos',    'icon': 'mail',           'link': '/admin/contato/mensagem/'},
                ],
            },
        ],
    },
}

# ─── Segurança em produção (atrás do Nginx com HTTPS) ─────────────────────────
if not DEBUG:
    # O Nginx avisa o Django que a requisição original veio por HTTPS
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = True

    # Ative (=True no .env) só DEPOIS que o certificado SSL estiver instalado
    HTTPS_ENABLED = config('HTTPS_ENABLED', default=False, cast=bool)
    SESSION_COOKIE_SECURE = HTTPS_ENABLED
    CSRF_COOKIE_SECURE = HTTPS_ENABLED
    SECURE_SSL_REDIRECT = False          # o redirecionamento HTTP→HTTPS é feito pelo Nginx
    SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=0, cast=int)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'same-origin'
    X_FRAME_OPTIONS = 'DENY'

# ─── Logs (aparecem no journalctl do serviço gunicorn) ────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {'handlers': ['console'], 'level': 'WARNING'},
    'loggers': {
        'django': {'handlers': ['console'], 'level': config('DJANGO_LOG_LEVEL', default='INFO'), 'propagate': False},
    },
}

if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
