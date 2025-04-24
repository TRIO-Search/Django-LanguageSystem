# **Django i18n 语言切换功能开发文档**

**注意:** 本 README 中的代码示例已链接到项目仓库中的实际文件。请将 YOUR\_GITHUB\_REPO\_URL 替换为您实际的仓库地址。

## **目录**

* [功能概述](#bookmark=id.44z6lue823m0)  
* [开发环境配置](#bookmark=id.2w0p24vcu9e0)  
* [核心实现步骤](#bookmark=id.qg3q2sesdvh1)  
* [生产环境部署](#bookmark=id.o2kox1sawso4)  
* [维护指南](#bookmark=id.scduzjoncstr)  
* [常见问题排查](#bookmark=id.108eoxhisz4o)

## **功能概述**

实现多语言切换系统，支持：

* 中英文双语切换  
* 用户个人语言偏好保存  
* 动态内容国际化  
* 生产环境无缝部署

## **开发环境配置**

### **系统依赖**

\# Ubuntu/WSL  
\# GNU gettext 工具集，这是Django国际化(i18n)的底层依赖，若项目要部署在服务器上则需要在服务器也下载此工具集  
sudo apt-get install gettext  
\# 示例Django项目所用版本为5.2 (请根据你的项目调整)  
python \-m pip install django==5.2

### **项目结构（示例）**

my-project/               \# 项目根目录 (根据你的实际名称)  
├── locale/               \# 翻译文件目录  
│   └── zh\_Hans/          \# 简体中文 (或其他语言代码, 如 en)  
│       └── LC\_MESSAGES/  
│           ├── django.po \# 翻译模板文件  
│           └── django.mo \# 编译后的翻译文件  
├── accounts/             \# 示例应用  
│   ├── models.py  
│   ├── views.py  
│   └── urls.py  
│   └── forms.py  
├── templates/            \# HTML 模板目录  
│   ├── base.html         \# 基础模板  
│   └── accounts/  
│       └── profile.html  \# 示例模板  
├── myproject/            \# Django 项目配置目录  
│   └── settings/  
│       └── base.py       \# 基础配置  
├── manage.py  
└── ... (其他文件)

## **核心实现步骤**

### **一. 基础配置 (myproject/settings/base.py)**

进行语言切换开发必须的基础配置，包括启用 i18n、设置语言、定义 LOCALE\_PATHS 和添加 LocaleMiddleware。

➡️ **查看 myproject/settings/base.py 代码**: [YOUR\_GITHUB\_REPO\_URL/blob/main/myproject/settings/base.py]([http://docs.google.com/YOUR_GITHUB_REPO_URL/blob/main](https://github.com/F16TH/my-project/tree/main/myproject/settings/base.py)

### **二. 语言切换视图 (accounts/views.py)**

处理用户语言选择、设置 session 和 cookie，并重定向回原页面的视图函数 (set\_language)。

➡️ **查看 accounts/views.py 代码**: [YOUR\_GITHUB\_REPO\_URL/blob/main/accounts/views.py](https://github.com/F16TH/my-project/tree/main/accounts/views.py)

### **三. 语言切换 URL 配置 (accounts/urls.py)**

将 set\_language 视图函数连接到特定的 URL 路径。

➡️ 查看 accounts/urls.py 代码: YOUR\_GITHUB\_REPO\_URL/blob/main/accounts/urls.py  
(注意：你还需要在项目主 urls.py 中 include 这个应用的 URL 配置)

### **四. 模板语言切换控件 (templates/base.html)**

在 HTML 基础模板中添加一个表单，允许用户选择语言。该表单会提交到 set\_language 视图。

➡️ **查看 templates/base.html 代码**: [YOUR\_GITHUB\_REPO\_URL/blob/main/templates/base.html](https://github.com/F16TH/my-project/tree/main/templates/base.html)

### **五. 标记需要翻译的字符串**

#### **1\. HTML 模板 (.html 文件)**

使用 {% load i18n %} 加载标签库，并使用 {% trans "..." %} 或 {% blocktrans %} ... {% endblocktrans %} 标记需要翻译的文本。

➡️ **查看 templates/accounts/profile.html 示例代码**: [https://github.com/F16TH/my-project/tree/main/templates/accounts/profile.html](https://github.com/F16TH/my-project/tree/main/templates/accounts/profile.html)

#### **2\. Python 代码 (.py 文件)**

导入 gettext\_lazy as \_，并使用 \_("...") 标记模型字段、表单标签、视图消息等需要翻译的字符串。

➡️ 查看 accounts/models.py 示例代码: https://github.com/F16TH/my-project/tree/main/accounts/models.py  
➡️ 查看 accounts/forms.py 示例代码: https://github.com/F16TH/my-project/tree/main/accounts/forms.py

### **六. 生成和编译翻译文件**

#### **1\. 生成翻译文件 (.po)**

在项目根目录运行命令以扫描代码和模板，生成或更新 .po 文件。

\# 为简体中文生成/更新 .po 文件  
python manage.py makemessages \-l zh\_Hans \--ignore=venv

\# 为所有语言生成/更新 .po 文件  
python manage.py makemessages \-a \--ignore=venv

#### **2\. 编辑翻译文件 (.po)**

手动编辑 locale/\<lang\>/LC\_MESSAGES/django.po 文件，在 msgstr 行填入翻译。

➡️ **查看 locale/zh\_Hans/LC\_MESSAGES/django.po 示例文件**: [YOUR\_GITHUB\_REPO\_URL/blob/main/locale/zh\_Hans/LC\_MESSAGES/django.po](https://github.com/F16TH/my-project/tree/main/locale/zh_Hans/LC_MESSAGES/django.po)

#### **3\. 编译翻译文件 (.mo)**

运行命令将编辑好的 .po 文件编译成 Django 使用的 .mo 二进制文件。

python manage.py compilemessages \--ignore=venv

编译后的 .mo 文件通常不建议直接提交到版本控制中（但 .po 文件应该提交），因为它们是生成文件。

## **生产环境部署 (示例: Nginx \+ Gunicorn)**

确保服务器上已安装 gettext 工具集。

### **Nginx 配置**

关键是传递 Accept-Language 头。

location / {  
    \# ... 其他 proxy 设置 ...  
    proxy\_set\_header Accept-Language $http\_accept\_language; \# 传递浏览器语言偏好  
    proxy\_pass http://unix:/path/to/your/project/myproject.sock; \# 根据实际情况修改 socket 路径  
}

➡️ 查看示例 Nginx 配置文件 (deploy/nginx.conf): YOUR\_GITHUB\_REPO\_URL/blob/main/deploy/nginx.conf  
(这是一个示例路径，请根据你的项目调整或创建)

### **Gunicorn 配置**

通常不需要特殊配置，确保 Gunicorn 能加载 Django 配置即可。

\# 示例 Gunicorn 启动命令  
gunicorn myproject.wsgi:application \--bind unix:/path/to/your/project/myproject.sock ... \# 根据实际情况修改

➡️ 查看示例 Gunicorn 启动脚本 (deploy/gunicorn\_start.sh): YOUR\_GITHUB\_REPO\_URL/blob/main/deploy/gunicorn\_start.sh  
(这是一个示例路径，请根据你的项目调整或创建)

## **维护指南**

* **定期更新翻译:** 修改文本后，运行 makemessages \-\> 编辑 .po \-\> compilemessages。  
* **代码审查:** 检查翻译标记的使用。  
* **测试:** 在不同语言下测试。  
* **备份:** 备份 locale 目录 (尤其是 .po 文件)。

## **常见问题排查**

* **翻译不生效:** 检查 settings.py, MIDDLEWARE, LOCALE\_PATHS, .po 文件编辑和 .mo 文件编译，重启服务器，清缓存/Cookie。  
* **makemessages 找不到字符串:** 检查标记是否正确，命令运行目录，--ignore 参数。  
* **.po 文件语法错误:** 使用 msgfmt \-c 检查。  
* **部分内容未翻译:** 检查是否所有相关文本都已标记。
