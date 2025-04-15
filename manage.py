#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

def set_default_settings():
    """
    自动设置默认的DJANGO_SETTINGS_MODULE
    规则：
    1. 如果已设置环境变量，则优先使用
    2. 如果是runserver命令，默认使用开发配置
    3. 其他情况使用生产配置
    """
    default_settings = 'myproject.settings.prod'  # 默认生产环境
    if 'runserver' in sys.argv:
        default_settings = 'myproject.settings.dev'  # 开发命令使用开发配置
    
    # 如果环境变量未设置，则使用默认配置
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', default_settings)

def main():
    """Run administrative tasks."""
    # 先设置默认配置
    set_default_settings()
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # 检查生产环境配置安全性
    if 'myproject.settings.prod' in os.environ['DJANGO_SETTINGS_MODULE']:
        check_production_safety()
    
    execute_from_command_line(sys.argv)

def check_production_safety():
    """检查生产环境关键配置"""
    from django.conf import settings
    if settings.DEBUG:
        print("\n⚠️ 警告：生产环境DEBUG模式已启用！这非常不安全！\n")
    if '*' in settings.ALLOWED_HOSTS:
        print("\n⚠️ 警告：ALLOWED_HOSTS包含通配符'*'！这存在安全风险！\n")

if __name__ == '__main__':
    main()
