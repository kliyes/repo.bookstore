#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.
# Django settings for basic pinax project.

import os.path
import posixpath

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# log level on console
LOG_LEVEL = 'INFO'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# tells Pinax to serve media through the staticfiles app.
SERVE_MEDIA = DEBUG

# django-compressor is turned off by default due to deployment overhead for
# most users. See <URL> for more information
COMPRESS = False

# to solove calling some URL via POST, but the URL doesn't end in a slash and you 
# have APPEND_SLASH set, like using /account/login without end slash 
#APPEND_SLASH=True  #added by junn

# 
#CSRF_COOKIE_NAME = "csrftoken"

INTERNAL_IPS = [
    "127.0.0.1",
]

ADMINS = [
    ("Admin", "jingyang.tom@qq.com"),
]

CONTACT_EMAIL = 'support@bookstore.com'

MANAGERS = ADMINS

# added for compatibling for django1.4.2
DATABASE_ENGINE = {}

DATABASES = {
    "default": {
        "ENGINE": 'django.db.backends.sqlite3', # Add "postgresql_psycopg2", "postgresql", "mysql", "sqlite3" or "oracle".
        "NAME": '/home/kliyes/data/bookstore.db',              # Or path to database file if using sqlite3.
        "USER": '',                       # Not used with sqlite3.
        "PASSWORD": '',              # Not used with sqlite3.
        "HOST": '',                  # Set to empty string for localhost. Not used with sqlite3.
        "PORT": '',                       # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
#TIME_ZONE = "US/Eastern"
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
#LANGUAGE_CODE = "en-us"
LANGUAGE_CODE = "zh_CN"

# Added by jun
ugettext = lambda s: s

LANGUAGES = [
    ("zh_CN", u"Chinese"),
    ("en", u"English")
]

# 1-xizhi.com
SITE_ID = 1

# 站点是否正在维护中,默认False
IS_SITE_MAINTAINED = False

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
MEDIA_ROOT = "/home/kliyes/media/"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
MEDIA_URL = "/media/"

# Absolute path to the directory that holds static files like app media.
STATIC_ROOT = os.path.join(PROJECT_ROOT, "static")

# URL that handles the static files like app media.
STATIC_URL = "/static/"   

# Additional directories which hold static files
STATICFILES_DIRS = [
    #os.path.join(PROJECT_ROOT, "static"), # maybe this is not needed , by jun
]

STATICFILES_FINDERS = [
    "staticfiles.finders.FileSystemFinder",
    "staticfiles.finders.AppDirectoriesFinder",
    "staticfiles.finders.LegacyAppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to us_(u"small picture path"), e a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = posixpath.join(STATIC_URL, "admin/")

# Subdirectory of COMPRESS_ROOT to store the cached media files in
COMPRESS_OUTPUT_DIR = "cache"

# Make this unique, and don't share it with anybody.
SECRET_KEY = "-%(d@_ict!bx((mskt09(^u%*u14vx)nhw^li87ul=_kw_5adr"

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]

MIDDLEWARE_CLASSES = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_openid.consumer.SessionConsumer",
    "django.contrib.messages.middleware.MessageMiddleware",
    #"pinax.apps.account.middleware.LocaleMiddleware",
    "account.middleware.LocaleMiddleware",
    "pagination.middleware.PaginationMiddleware",
    "pinax.middleware.security.HideSensistiveFieldsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    
    # added by junn
    "onlineuser.middleware.OnlineUserMiddleware",
]

ROOT_URLCONF = "bookstore.urls"

TEMPLATE_DIRS = [
    os.path.join(PROJECT_ROOT, "templates"),
]

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    
    "staticfiles.context_processors.static",
    
    "pinax.core.context_processors.pinax_settings",
    
    "pinax.apps.account.context_processors.account",
    
    "notification.context_processors.notification",
    "announcements.context_processors.site_wide_announcements",
    
    #added by junn
    "profiles.context_processors.get_profile",
    "profiles.context_processors.getNoticeCount",
    "context_processors.importSettings",
]

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
    "onlineuser",
    
    # django wsgi server
    #"gunicorn",
    "widget_tweaks",  #to add attrs on html page, not in python form code
     
    "common",
    "account",
    "profiles",
    #"activity",
    "books", 
    "sites", 
]

FIXTURE_DIRS = [
    os.path.join(PROJECT_ROOT, "fixtures"),
]

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"


ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda o: "/profiles/profile/%s/" % o.username,
}

AUTH_PROFILE_MODULE = "profiles.Profile"
NOTIFICATION_LANGUAGE_MODULE = "account.Account"

ACCOUNT_OPEN_SIGNUP = False
ACCOUNT_USE_OPENID = False

ACCOUNT_UNIQUE_EMAIL = EMAIL_CONFIRMATION_UNIQUE_EMAIL = False

#modified by jun
AUTHENTICATION_BACKENDS = [
    "account.auth_backends.AuthenticationBackend",
]

HOME_URL = "/"
LOGIN_URL = "/account/login/"
SIGNUP_URL = "/account/signup/"
LOGIN_REDIRECT_URLNAME = "welcome"
SIGNUP_REDIRECT_URLNAME = "welcome"
LOGOUT_REDIRECT_URLNAME = "welcome"

EMAIL_DEBUG = DEBUG

DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False,
}


""" 
Email config 
"""
ACCOUNT_REQUIRED_EMAIL = True           #Email是否必需
ACCOUNT_EMAIL_AUTHENTICATION = True     #是否需要Email登录验证
ACCOUNT_EMAIL_VERIFICATION = True       #账号是否需要邮件激活
EMAIL_CONFIRMATION_DAYS = 7
MAX_EMAIL_SENT_COUNT_PERDAY = 5         #每个邮箱每天最大接收邮件次数

#密码重置邮件主题
EMAIL_CONFIRMATION_SUBJECT = u"激活账号｜BookStore"
PASSWD_RESET_SUBJECT = u"密码重置｜BookStore"

# email message template setup
EMAIL_CONFIRMATION_MESSAGE = "account/mailtemplates/email_confirmation_message.txt"
PWD_RESET_MSG = "account/mailtemplates/password_reset_message.txt"

# reserved_words, 保留域名字符串,用户设置个性域名时不允许被使用
RESERVED_WORDS = [
                   
]

# Email server setup
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.dannysite.net' 
EMAIL_PORT = 25   
DEFAULT_FROM_EMAIL = 'service@kliyes.com'
EMAIL_HOST_USER='postman'
EMAIL_HOST_PASSWORD='Zdnhvk6BLgU2QyP8'
EMAIL_USE_TLS = True

# Default Picture setup
DEFAULT_PIC = "default_pic"
DEFAULT_PIC_NORMAL = "default_pic_normal"
DEFAULT_PIC_SMALL = "default_pic_small"
DEFAULT_POSTER = "default_poster"
DEFAULT_POSTER_NORMAL = "default_poster_normal"
DEFAULT_POSTER_SMALL = "default_poster_small"

DEFAULT_IMG = "default_img"

#上传图片大小限制
PIC_UPPER_BOUND = 2  # 2M
POSTER_UPPER_BOUND = 5 #5M

ALLOWED_IMG_FORMAT = (".jpg", ".jpe", ".gif", ".jpeg", ".bmp", ".png")

PIC_ROOT = os.path.join(MEDIA_ROOT, "img")

BOOKPIC_ROOT = os.path.join(PIC_ROOT, "books")
USERPIC_ROOT = os.path.join(PIC_ROOT, "profiles")

SBPIC_ROOT = os.path.join(BOOKPIC_ROOT, "small")  # 书籍小图
MBPIC_ROOT = os.path.join(BOOKPIC_ROOT, "medium") # 书籍中图
LBPIC_ROOT = os.path.join(BOOKPIC_ROOT, "large")  # 书籍大图

SUPIC_ROOT = os.path.join(USERPIC_ROOT, "small")  # 用户小图
MUPIC_ROOT = os.path.join(USERPIC_ROOT, "medium") # 用户中图
LUPIC_ROOT = os.path.join(USERPIC_ROOT, "large")  # 用户大图

# Picture size
PIC_SIZE_BIG = (330, 330)         #大图像素宽高
PIC_SIZE_NORMAL = (128, 128)        #中图像素宽高
PIC_SIZE_SMALL = (64, 64)           #小图像素宽高

# Poster size(海报尺寸)
POSTER_SIZE_BIG = (330, 330)
POSTER_SIZE_NORMAL = (128, 128)
POSTER_SIZE_SMALL = (64, 64) 


## pagination params 
AFTER_RANGE_NUM = 6     #当前页前显示的页号个数 
BEFORE_RANGE_NUM = 6    #当前页后显示的页号个数 

## other paging params samples


## 是否允许注册.
SIGNUP_ALLOWED = True   # 置为True，则所有人都可注册。置为False,当且仅当登录状态admin可注册

#用于统计当前在线用户数，所配置的时间间隔内登录过的用户都计为当前在线用户，单位秒(s)
LAST_ONLINE_DURATION = 600  
   
#线程每次循环等待时间, 单位：秒， added by danny
THREAD_SLEEP_TIME = 5
#初始启动的线程数, added by danny
MIN_THREADS_NUM = 2
MAX_THREADS_NUM = 10   

BACK_GROUND = (255,255,255)
LINE_COLOR = (0, 0, 0)
IMG_WIDTH = 120
IMG_HEIGHT = 40
#FONT_COLOR =['#000', '#16496b', '#666']  # also can set to 
FONT_COLOR = ['darkblue','blue'] 
FONT_SIZE = 30
FONT_PATH = "static/lershare/font/arial.ttf"
CHAR_RANGE = '0123456789AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'

########### The following global data is initialized while related class imported 
CACHED_CITIES = {}          # 所有城市
CACHED_AREAES = {}          # 所有城市区域
CACHED_TAGS = {}            # 所有个性标签
CACHED_ACTIVITY_TAGS = {}   # 所有活动标签
CACHED_CLIENTS = {}         # 所有客户端(访问key值)

TEMPLATE_TEST = "tests/login.html"

# Start threads to get the waiting-send emails and to sent them
#from account.threads import run_email_sending_thread
#run_email_sending_thread()
# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
    #from log_config import *
    from template_settings import *
    from local_settings import *      
except ImportError:
    pass
