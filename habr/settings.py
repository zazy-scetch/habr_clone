import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

with open(BASE_DIR.joinpath("secret.json"), "r") as secret_file:
    secret_value = json.load(secret_file)

SECRET_KEY = secret_value["SECRET_KEY"]

DEBUG = secret_value.get("DEBUG", True)

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.authorization",
    "apps.articles",
    "apps.account",
    "apps.comments",
    "ckeditor",
    "ckeditor_uploader",
    "social_django",
    "apps.moderator",
]
# для postgresql добавить psycopg2

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
]

ROOT_URLCONF = "habr.urls"

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            TEMPLATE_DIR,
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.articles.context_processors.get_all_hubs",
                "apps.moderator.context_processors.check_is_staff",
                "apps.moderator.context_processors.check_is_banned",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

WSGI_APPLICATION = "habr.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    },

    # "default": {
    #     "ENGINE": "django.db.backends.postgresql",
    #     "NAME": secret_value["DATABASE_NAME"],
    #     "USER": secret_value["DATABASE_USER"],
    #     "PASSWORD": secret_value["DATABASE_PASSWORD"],
    #     # "HOST": secret_value["DATABASE_HOST"],
    #     # "PORT": secret_value["DATABASE_PORT"],
    # },
}
# переключение настроек на postgresql
# DATABASES["default"] = DATABASES["postgresql"]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
STATIC_ROOT = os.path.join(BASE_DIR, "static_dev")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

CKEDITOR_UPLOAD_PATH = "uploads/"
# CKEDITOR_UPLOAD_SLUGIFY_FILENAME = False
CKEDITOR_RESTRICT_BY_USER = False
CKEDITOR_ALLOW_NONIMAGE_FILES = False
CKEDITOR_IMAGE_BACKEND = "pillow"

CKEDITOR_CONFIGS = {
    "for_user": {
        'skin': 'moono-lisa',
        # 'contentsCss': ['/static/css/style.min.css'],
        'toolbar': [
            [
                'Undo', 'Redo',
                '-', 'Format',
                '-', 'FontSize',
                '-', 'Blockquote',
                '-', 'Bold', 'Italic', 'Underline',
                '-', 'HorizontalRule',
                '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock',
                '-', 'NumberedList', 'BulletedList',
                '-', 'Image',
                '-', 'Source'
            ]
        ],
        'height': 500,
        'width': '100%',
        'toolbarCanCollapse': False,
        'forcePasteAsPlainText': True
    },
    "default": {
        "toolbar": "full",
        "height": 800,
        "width": 800,
    },
}

# используем своё приложение для аутентификации
AUTH_USER_MODEL = "authorization.HabrUser"

# нововведение в джанго 3.2
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Set login path:
#   https://docs.djangoproject.com/en/2.2/ref/settings/#login-url
LOGIN_URL = "apps.authorization:login"

LOGIN_ERROR_URL = '/'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

if DEBUG:
    DOMAIN_NAME = 'http://localhost:8000'

# Запуск локального smtp сервера: python3 -m smtpd -n -c DebuggingServer localhost:25
# Настройки для вывода сообщений о подтверждении регистрации в лог-файл\консоль
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = None
EMAIL_HOST_PASSWORD = None
EMAIL_USE_SSL = False
# вариант включения логгирования сообщений почты ввиде файлов
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = 'tmp/email-messages/'

## Рабочие настройки для работы через яндекс
# DEFAULT_FROM_EMAIL = secret_value["EMAIL_HOST_USER"]
# EMAIL_HOST = 'smtp.yandex.ru'
# EMAIL_PORT = 465
# EMAIL_HOST_USER = secret_value["EMAIL_HOST_USER"]
# EMAIL_HOST_PASSWORD = secret_value["EMAIL_HOST_PASSWORD"]
# EMAIL_USE_SSL = True

SOCIAL_AUTH_URL_NAMESPACE = 'social'

AUTHENTICATION_BACKENDS = [
    'social_core.backends.vk.VKOAuth2',
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]
SOCIAL_AUTH_VK_OAUTH2_IGNORE_DEFAULT_SCOPE = True
SOCIAL_AUTH_VK_OAUTH2_SCOPE = ['email']
SOCIAL_AUTH_VK_OAUTH2_KEY = secret_value['SOCIAL_AUTH_VK_OAUTH2_KEY']
SOCIAL_AUTH_VK_OAUTH2_SECRET = secret_value['SOCIAL_AUTH_VK_OAUTH2_SECRET']

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = secret_value['SOCIAL_AUTH_GOOGLE_OAUTH2_KEY']
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = secret_value['SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET']

SOCIAL_AUTH_GITHUB_IGNORE_DEFAULT_SCOPE = True
SOCIAL_AUTH_GITHUB_SCOPE = ['user:email']
SOCIAL_AUTH_GITHUB_KEY = secret_value['SOCIAL_AUTH_GITHUB_KEY']
SOCIAL_AUTH_GITHUB_SECRET = secret_value['SOCIAL_AUTH_GITHUB_SECRET']


SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'apps.authorization.pipeline.save_user_profile',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)
