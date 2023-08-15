
"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 3.2.16.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-=(b25g*p6(_m=+z@d(k_v_9$j*#nu74ci7=h0bzzi_yoxvy0_0'
GMAPS_KEY = 'AIzaSyBpLruvn_7H-6Q9gYl8LNGhVTm4kR5_2HY'#LINE Channel資料


#判斷乘客司機
LINE_CHANNEL_DATA = {
    'DriverServer':{
        'ACCESS_TOKEN':"szpnvewOfvOFrbgMFOnHU1TX1EjMywAX6NufOLrELgVW0WmZe1lQNc0WX8i1zYIpjzjtDYNBHTHJdDL97cLZ6+c7wGKLSsCrxqG1rVCCukeDiOVmOCck1gXL2WmKBLXzR3/lzWpIqpUJ0iroxZY3TgdB04t89/1O/w1cDnyilFU=",
        'SECRET':'aca858c32c1a29202b200e3db0685c98'
    },
      'Develope_passenger_server':{
        'ACCESS_TOKEN':"CZfTc72jI6v7Cm4PCkALF6GhlDOUhtMKYRi/IGtuh36zkcx+8bvyTIIWOOY+TACfEHmvzVkBb0WAG1S/62HGJ3lAKpKjV5g0fd5szviHe/H2cZwyD8StZFydHBEe8DSWMr11IzaaX4sIlFV1UOj3DQdB04t89/1O/w1cDnyilFU=",
        'SECRET':"7e4ef93671d3c6b100cbfa04be1224e8"
    }
}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "Develope_passenger_server",
    "goddess_taxi_server",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
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

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '35.234.48.3', # 替換為你的Cloud SQL連線名稱
        'POST': '3306',
        'NAME': 'goddess-taxi-sql',  # 替換為你的MySQL資料庫名稱
        'USER': 'goddess.taxi.admin',  # 替換為你的MySQL資料庫使用者名稱
        'PASSWORD': "k-qIiDG[B|qhVq[,",  # 替換為你的MySQL資料庫密碼
        'OPTIONS': {
            'charset': 'utf8mb4',  # 如果需要支援中文，使用utf8mb4編碼
        },
    }
}




# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'zh-Hant'

TIME_ZONE = 'Asia/Taipei'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATIC_ROOT = 'static/'
STATIC_URL = '/static/'
MEDIA_URL = '/media/'


STATICFILES_DIRS = [
    os.path.join(BASE_DIR,'statics'),
]

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
