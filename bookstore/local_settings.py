#coding=utf-8
import os

# override the default testrunner, which would create temp database while running
# testcase. If test other models which need the temp database, this need to be commented
TEST_RUNNER = 'tests.testrunner.NoDbTestRunner'

# database setting
DATABASES = {
    "default": {
        "ENGINE": 'django.db.backends.mysql',
        "NAME": 'bookstore',
        "USER": 'root',
        "PASSWORD": 'root',
        "HOST": '127.0.0.1',
        "PORT": '3306',
    }
}

# Memcached
#DEFAULT_CACHE_TIME_OUT = 600
#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#        'LOCATION': 'localhost:11211',
#        'TIMEOUT': DEFAULT_CACHE_TIME_OUT, 
#    }
#}

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.humanize",

    "pinax.templatetags",
    "pinax.apps.signup_codes",
    "pinax_theme_bootstrap",
    
    # external
    "notification", # must be first
    "staticfiles",
    "compressor",
    "debug_toolbar",
    "mailer",
    "django_openid",
    "timezones",
    "emailconfirmation",
    "announcements",
    "pagination",
    "idios",
    "metron",
    "PIL",
    #"onlineuser",
    
    # django wsgi server
    #"gunicorn",
     'widget_tweaks',  #to add attrs on html page, not in python form code
    
    # xizhi api project
    "common",
    "protocol",
    "api",
    "account",
    "profiles",
    "activity",
]

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

TEMPLATE_DIRS = [
    os.path.join(PROJECT_ROOT, "templates"),
]

# 1-xizhi.com 2-192.168.1.114:8000  4-192.168.1.112:8000 9-localhost:8000
SITE_ID = 4  
#SITE_ID = 9

CONTACT_EMAIL = 'support@localhost:8000'

#账号是否需要Email激活
ACCOUNT_EMAIL_VERIFICATION = True

# 验证邮件有效天数  
EMAIL_CONFIRMATION_DAYS = 3

# smtp setup
EMAIL_HOST = 'smtp.qq.com'  
EMAIL_PORT = 25
DEFAULT_FROM_EMAIL = 'no-reply@lianbi.com.cn'
EMAIL_HOST_PASSWORD = 'xz_noreply1012'
EMAIL_USE_TLS = False

# 是否允许注册
SIGNUP_ALLOWED = True 

DEBUG = True

# user uploaded file setup
MEDIA_ROOT = "E:/media/"
PIC_ROOT = os.path.join(MEDIA_ROOT, "img")

#test tempalte
TEMPLATE_TEST = "tests/login.html"
#http://192.168.1.50:8888/test/html/
#TEMPLATE_TEST = "protocol/clients.html"

