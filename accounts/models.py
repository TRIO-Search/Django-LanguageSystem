from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # 自定义字段
    bio = models.TextField(_('Personal Profile'), blank=True,
                          help_text=_('Write something about yourself'))  # 补充帮助文本翻译
    avatar = models.ImageField(_('Avatar'), upload_to='avatars/', blank=True,  # 首字母大写保持一致性
                             default='avatars/default_avatar.png',
                             help_text=_('Profile picture image'))
    website = models.URLField(_('Personal Website'), blank=True,
                            help_text=_('Your personal or professional website'))

    # 重定义多对多关系（补充翻译）
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text=_('The groups this user belongs to. A user will get all permissions granted.'),
        verbose_name=_('groups')
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text=_('Specific permissions for this user.'),
        verbose_name=_('user permissions')
    )

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')  # 明确复数形式
    
    def __str__(self):
        return self.username

class UserDocument(models.Model):
    owner = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        verbose_name=_('Owner')  # 翻译字段标签
    )
    uuid = models.UUIDField(
        default=uuid.uuid4, 
        editable=False, 
        unique=True, 
        verbose_name=_('Document ID')  # 翻译技术标识
    )
    document = models.FileField(
        upload_to='user_docs/%Y/%m/%d/',
        verbose_name=_('Document File'),
        help_text=_('Upload PDF, DOCX or TXT files')  # 添加帮助文本
    )
    title = models.CharField(
        max_length=100, 
        default=_('Untitled Document'),  # 默认值也需要翻译
        verbose_name=_('Document Title')
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_('Upload Time')
    )

    class Meta:
        verbose_name = _('User Document')  # 国际化单数名
        verbose_name_plural = _('User Documents')  # 国际化复数名

    def __str__(self):
        # 保持英文日志输出（系统内部使用）
        return f"{self.title} ({self.owner.username})"