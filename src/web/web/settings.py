"""
Django settings for web project.

Generated by 'django-admin startproject' using Django 1.9.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.urls import reverse_lazy

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '4cqgaa_*t1zj=x0-1djgxr=@h^b#9$r41()k*sani9m31pd$^%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bwb',
    'bwb_api',
    'bwb_webapp',
    'bootstrap3'
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'web.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True


_APP_NAME = 'Watson - The Marvel Cinematic Universe Expert'
_ORGANISATION_NAME = 'Language Technology group, Computer Science Department, TU Darmstadt.'
_IMPRINT_URL = ''
_REPO_URL = 'https://github.com/bhaettasch/watson-domain-expert-chatbot'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = 'static'

MEDIA_ROOT = 'upload/'
MEDIA_URL = '/media/'

LOGIN_URL = reverse_lazy('app:login')


"""
----------------------------------------------------------------------------------------
CUSTOM Settings
----------------------------------------------------------------------------------------
"""

API_KEY_ALCHEMY = "Replace with your key in local settings"

PRIVATE_INSTANCE_URL = ''
PRIVATE_INSTANCE_USER = ''
PRIVATE_INSTANCE_PW = ''

T2S_URL = ''
T2S_USER = ''
T2S_PW = ''
T2S_VOICE = 'en-US_AllisonVoice'

API_KEY_YOUTUBE = ''
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

S2T_URL = ''
S2T_USER = ''
S2T_PW = ''

"""
----------------------------------------------------------------------------------------
Local settings loader

Add a settings_local.py file to the current folder to store local settings (not synced
to the repository). This should hold all sensitive data like API keys.
----------------------------------------------------------------------------------------
"""

try:
    from .settings_local import *
except ImportError:
    pass
