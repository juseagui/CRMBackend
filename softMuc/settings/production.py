from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['crm-env-5.eba-tvvqfm3m.us-west-2.elasticbeanstalk.com']

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'db_softmuc',
        'USER': 'admin',
        'PASSWORD': 'Developer1144198690',
        'HOST': 'database-crm.caik5hlqn9fy.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
    },
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
