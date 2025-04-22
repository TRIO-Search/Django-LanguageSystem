from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserDocument

#注册自定义用户模型到后台
admin.site.register(CustomUser, UserAdmin)

#注册文档模型到后台
@admin.register(UserDocument)
class UserDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'uploaded_at')
    search_fields = ('title', 'owner__username')
