from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

#注册自定义用户模型
admin.site.register(CustomUser, UserAdmin)

# Register your models here.
