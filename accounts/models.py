from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class CustomUser(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    #自定义字段
    bio = models.TextField('个人简介',blank=True)
    avatar = models.ImageField('头像',upload_to='avatars/',blank=True, default='avatars/default_avatar.png')
    website = models.URLField('个人网站',blank=True)

    #重定义多对多关系
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    #元数据
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return self.username

# Create your models here.

