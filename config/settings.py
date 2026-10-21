"""تنظیمات پروژهٔ یدک‌پخش (Django)."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _secret():
    env = os.environ.get('DJANGO_SECRET_KEY')
    if env:
        return env
    f = BASE_DIR / '.secret_key'
    if f.exists():
        return f.read_text().strip()
    import secrets
    key = secrets.token_urlsafe(60)
    f.write_text(key)
    return key


SECRET_KEY = _secret()
DEBUG = os.environ.get('DJANGO_DEBUG', '1') == '1'
ALLOWED_HOSTS = ['*'] if DEBUG else [h for h in os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',') if h]
CSRF_TRUSTED_ORIGINS = [o for o in os.environ.get('DJANGO_CSRF_ORIGINS', '').split(',') if o]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shop',
    'orders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'orders.middleware.AdminEnglishMiddleware',   # پنل مدیریت انگلیسی
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'orders.middleware.CustomerGateMiddleware',   # ورود با موبایل اجباری؛ بعد از ورود همهٔ سایت باز است
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
        'shop.context.site',
    ]},
}]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}

AUTH_PASSWORD_VALIDATORS = []  # رمز مدیر را خودتان انتخاب می‌کنید؛ برای سایت واقعی رمز قوی بگذارید

LANGUAGE_CODE = 'fa'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SESSION_COOKIE_AGE = 60 * 60 * 24 * 30
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# --- پیامک ورود ---
# console: کد روی صفحهٔ ورود نمایش داده می‌شود (فقط برای تست!)   |   kavenegar: ارسال واقعی پیامک
SMS_BACKEND = os.environ.get('SMS_BACKEND', 'melipayamak')
# Melipayamak OTP address (contains your secret token - do not share). Used when SMS_BACKEND = 'melipayamak'.
MELIPAYAMAK_OTP_URL = os.environ.get('MELIPAYAMAK_OTP_URL', 'https://console.melipayamak.com/api/send/otp/adbcfecfa9be4dd48691cf9f2b314cfe')
KAVENEGAR_API_KEY = os.environ.get('KAVENEGAR_API_KEY', '4A4176657541474937446978716D7A72564F4372753968586F3033333137674773354B50795A577A704E4D3D')
KAVENEGAR_TEMPLATE = os.environ.get('KAVENEGAR_TEMPLATE', 'verify')
# 'send' = plain SMS (works on the free/standard Kavenegar service). 'lookup' = template/verify method (needs the advanced service).
KAVENEGAR_METHOD = os.environ.get('KAVENEGAR_METHOD', 'send')
KAVENEGAR_SENDER = os.environ.get('KAVENEGAR_SENDER', '10004346')  # sender line number. 10004346 is the sample line from Kavenegar's own SDK docs - replace it with YOUR line from the Kavenegar panel
KAVENEGAR_MESSAGE = os.environ.get('KAVENEGAR_MESSAGE', 'کد ورود شما: {code}')

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
