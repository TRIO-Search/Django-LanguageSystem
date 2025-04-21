# myproject/settings/dev.py
from .base import *  # 导入所有基础配置

# 开发环境专用配置
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# SQLite数据库（开发用）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
STATICFILES_DIRS = [  # 开发环境专用
    os.path.join(BASE_DIR, 'static'),
]
# 本地开发的额外配置
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
 # 邮件输出到控制台
