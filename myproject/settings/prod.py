# myproject/settings/prod.py
from .base import *  # 导入所有基础配置

# 生产环境专用配置
DEBUG = False
ALLOWED_HOSTS = ['47.93.249.56','localhost','127.0.0.1']  # 你的VPS IP或域名

#生产环境的数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR / 'db.sqlite3'),
	'OPTIONS':{
	    'timeout':30,  #默认五秒延长避免锁冲突
	}
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, 'static')  # 生产环境收集静态文件用 

USE_X_FORWARDED_HOST = True  # 如果使用代理

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# 安全配置
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False  # 如果启用HTTPS就全改成True，这里是启用http
