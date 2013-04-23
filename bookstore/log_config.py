# -*- coding: utf-8 -*-

"""
Here setup the site log info
"""
import os

LOG_DIR = os.path.relpath('../../logs/')
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

# 日志文件路径
LOG_FILE_PATH = os.path.join(LOG_DIR, "bookstore.log")

# 日志显示级别
LOG_LEVEL = 'INFO'  #ERROR, INFO, DEBUG

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(pathname)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'file': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILE_PATH,
            'maxBytes': 2*1024*1024,
            'backupCount': 5,
            'formatter': 'standard',
        },
        'mail_admins': {  
            'level': 'ERROR',  
            'class': 'django.utils.log.AdminEmailHandler',  
            'include_html': True,  
        },  
        'console':{
            'level': LOG_LEVEL,
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers':['console','file'], # 同时写到console和文件里
            'propagate': True,
            'level':'DEBUG',
        },
        'django.request': {
            'handlers': ['console', 'mail_admins', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'mysite': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    }
}

# why both logger and handler need to setup log level ? 

