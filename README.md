# **Django i18n 语言切换功能开发文档**

## **目录**

* [功能概述](#功能概述)  
* [开发环境配置](#开发环境配置)  
* [核心实现步骤](#核心实现步骤)  
* [生产环境部署](#生产环境部署)  
* [维护指南](#维护指南)  
* [常见问题排查](#常见问题排查)

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

进行语言切换开发必须的基础配置，包括启用 i18n、设置语言、定义 LOCALE\_PATHS 和添加 LocaleMiddleware。下为示例

```python
# settings.py 或 settings/base.py

import os  
from django.utils.translation import gettext_lazy as _ # 翻译所需

# 项目根目录 (根据你的项目结构调整)  
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # 或者其他定义方式

# 启用 i18n 和 l10n  
USE_I18N = True  
USE_L10N = True # 通常与 USE_I18N 一起启用，用于格式化日期、数字等

# 默认语言  
LANGUAGE_CODE = 'zh-hans' # 设置项目默认语言

# 可用语言列表  
LANGUAGES = [  
    ('en', _('English')),         # 英文  
    ('zh-hans', _('Simplified Chinese')), # 简体中文  
    # ('ja', _('Japanese')), # 可以添加更多语言  
]

# 翻译文件路径  
LOCALE_PATHS = [  
    os.path.join(BASE\_DIR, 'locale'), # 指向包含各语言翻译文件的 'locale' 目录  
]

# 中间件配置  
MIDDLEWARE = [  
    # ... 其他中间件  
    'django.contrib.sessions.middleware.SessionMiddleware', # Session 中间件，必须在 LocaleMiddleware 之前  
    'django.middleware.locale.LocaleMiddleware',          # 核心：处理语言切换的中间件，必须在 SessionMiddleware 之后，CommonMiddleware 之前  
    'django.middleware.common.CommonMiddleware',  
    # ... 其他中间件  
]
```

➡️ **查看 myproject/settings/base.py 代码**: [my-project/myproject/settings/base.py](https://github.com/F16TH/my-project/tree/main/myproject/settings/base.py)

### **二. 语言切换视图 (accounts/views.py)**

处理用户语言选择、设置 session 和 cookie，并重定向回原页面的视图函数 (set\_language)。以下为示例，或者可查看本项目内函数

```python
# accounts/views.py (或项目内任何合适的位置)

from django.http import HttpResponseRedirect  
from django.urls import reverse  
from django.utils.translation import activate, check_for_language  
from django.conf import settings  
from django.views.decorators.http import require_POST  
from django.utils.http import url_has_allowed_host_and_scheme

@require_POST # 确保只接受 POST 请求  
def set_language(request):  
    """  
    视图函数，用于设置用户选择的语言。  
    """  
    lang_code = request.POST.get('language') # 从 POST 数据获取选择的语言代码  
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') # 获取重定向 URL

    # 校验 next_url 是否安全，防止开放重定向漏洞  
    # 注意：Django 4.0+ 需要提供 allowed_hosts  
    if not url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={request.get_host()}):  
        next_url = reverse('home') # 如果不安全，重定向到首页或其他安全页面

    # 检查语言代码是否在 settings.LANGUAGES 中定义  
    if lang_code and check_for_language(lang_code):  
        # 设置 session 中的语言  
        # Django 的 LocaleMiddleware 会查找 'django_language' 这个 session key  
        request.session[settings.LANGUAGE_SESSION_KEY] = lang_code  
        # 激活当前请求的语言 (可选，因为中间件会处理，但显式激活有时有用)  
        # activate(lang_code)

        # 创建重定向响应  
        response = HttpResponseRedirect(next\_url)

        # 设置语言 Cookie (LocaleMiddleware 也会自动处理，但手动设置可以控制更多参数)  
        response.set_cookie(  
            settings.LANGUAGE_COOKIE_NAME, # 使用 settings 中的 Cookie 名称  
            lang_code,  
            max_age=settings.LANGUAGE_COOKIE_AGE, # 使用 settings 中的有效期  
            path=settings.LANGUAGE_COOKIE_PATH,  
            domain=settings.LANGUAGE_COOKIE_DOMAIN,  
            secure=settings.LANGUAGE_COOKIE_SECURE,  
            httponly=settings.LANGUAGE_COOKIE_HTTPONLY,  
            samesite=settings.LANGUAGE_COOKIE_SAMESITE  
        )  
        return response  
    else:  
        # 如果语言代码无效，直接重定向  
        return HttpResponseRedirect(next_url)
```

➡️ **查看 accounts/views.py 代码**: [my-project/accounts/views.py](https://github.com/F16TH/my-project/tree/main/accounts/views.py)

### **三. 语言切换 URL 配置 (accounts/urls.py)**

将 set\_language 视图函数连接到特定的 URL 路径。以下为示例，或者可查看本项目代码

在项目的主 urls.py 或应用的 urls.py 中添加路径：

```python
# myproject/urls.py (主 URL 配置)  
from django.contrib import admin  
from django.urls import path, include  
from accounts.views import set_language # 导入视图

urlpatterns = [  
    path('admin/', admin.site.urls),  
    # ... 其他应用的 URL  
    # path('accounts/', include('accounts.urls')), # 如果 set_language 在 accounts.urls.py  
    path('i18n/setlang/', set_language, name='set_language'), # 直接在主 urls.py 定义  
]

# 或者在 accounts/urls.py 中定义  
# from django.urls import path  
# from . import views  
#  
# app_name = 'accounts' # 建议为应用 URL 设置命名空间  
# urlpatterns = [  
#     # ... 其他 accounts 的 URL  
#     path('setlang/', views.set_language, name='set_language'),  
# ]  
# 然后在主 urls.py 中 include: path('i18n/', include('accounts.urls')),  
# 模板中引用变为 {% url 'accounts:set_language' %}
```

➡️ 查看 accounts/urls.py 代码: [my-project/accounts/urls.py](https://github.com/F16TH/my-project/tree/main/accounts/urls.py)  
(注意：你还需要在项目主 urls.py 中 include 这个应用的 URL 配置)

### **四. 模板语言切换控件 (templates/base.html)**

在 HTML 基础模板中添加一个表单，允许用户选择语言。该表单会提交到 set\_language 视图。以下为示例，或者可查看本项目代码

```html
{# templates/base.html #}  
{% load i18n %} {# 加载 i18n 标签库 #}

<!DOCTYPE html>  
<html lang="{{ request.LANGUAGE_CODE }}"> {# 设置 html 标签的 lang 属性 #}  
<head>  
    <meta charset="UTF-8">  
    <title>{% trans "My Website" %}</title> {# 示例：翻译标题 #}  
</head>  
<body>  
    <header>  
        {# 语言切换表单 #}  
        <form action="{% url 'set_language' %}" method="post" style="display: inline;">  
            {% csrf_token %} {# CSRF 保护 #}  
            {# 隐藏字段，用于重定向回当前页面 #}  
            <input name="next" type="hidden" value="{{ request.get_full_path }}">

            <select name="language" onchange="this.form.submit()">  
                {% get_available_languages as LANGUAGES %} {# 获取可用语言 #}  
                {% get_current_language as CURRENT_LANG %} {# 获取当前语言 #}  
                {% for lang_code, lang_name in LANGUAGES %}  
                    <option value="{{ lang_code }}" {% if lang_code == CURRENT_LANG %}selected{% endif %}>  
                        {{ lang_name }} {# 显示语言名称 (例如 'English', '简体中文') #}  
                    </option>  
                {% endfor %}  
            </select>  
            {# (可选) 添加一个提交按钮，以防 JS 禁用 #}  
            {# <button type="submit">{% trans "Change Language" %}</button> #}  
        </form>  
        {# 其他 header 内容 #}  
        <h1>{% trans "Welcome to My Site" %}</h1>  
    </header>

    <main>  
        {% block content %}  
        {# 页面主要内容 #}  
        <p>{% trans "This is the main content area." %}</p>  
        {% endblock %}  
    </main>

    <footer>  
        {# Footer 内容 #}  
    </footer>  
</body>  
</html>
```

➡️ **查看 templates/base.html 代码**: [my-project/templates/base.html](https://github.com/F16TH/my-project/tree/main/templates/base.html)

### **五. 标记需要翻译的字符串**

#### **1\. HTML 模板 (.html 文件)**

使用 {% load i18n %} 加载标签库，并使用 {% trans "..." %} 或 {% blocktrans %} ... {% endblocktrans %} 标记需要翻译的文本。具体操作如下

**重要:** 在每个需要翻译的模板文件顶部添加 {% load i18n %}。

**a. 简单翻译 (trans)**

{% load i18n %}

\<h1\>{% trans "My Profile" %}\</h1\>  
\<p\>{% trans "This text will be translated." %}\</p\>  
\<button type="submit"\>{% trans "Save Changes" %}\</button\>

**b. 带变量的翻译 (trans 或 blocktrans)**

{% load i18n %}

{\# 使用 trans 标签 (简单变量) \#}  
\<p\>{% trans "Welcome back," %} {{ user.username }}\!\</p\>

{\# 使用 blocktrans 标签 (更清晰，尤其是有多个变量或 HTML 时) \#}  
{% blocktrans with username=user.username %}Hello {{ username }}, how are you?{% endblocktrans %}

{\# blocktrans 示例：包含 HTML \#}  
{% blocktrans %}You can \<a href="/profile/"\>edit your profile\</a\>.{% endblocktrans %}

**c. 块翻译 (blocktrans)** (用于多行文本或包含模板标签/过滤器)

{% load i18n %}

{\# 多行文本 \#}  
{% blocktrans %}  
This is the first line.  
This is the second line.  
{% endblocktrans %}

{\# 包含变量和过滤器 \#}  
{% blocktrans with user\_count=users|length %}  
There are {{ user\_count }} active users.  
{% endblocktrans %}

**d. 复数形式 (blocktrans 与 plural)**

{% load i18n %}

{% blocktrans count counter=documents.count %}  
You have 1 document.  
{% plural %}  
You have {{ counter }} documents.  
{% endblocktrans %}

{% blocktrans with amount=cart.total count items\_count=cart.items.count %}  
Your cart has {{ items\_count }} item. Total: ${{ amount }}.  
{% plural %}  
Your cart has {{ items\_count }} items. Total: ${{ amount }}.  
{% endblocktrans %}

**e. 添加翻译上下文 (pgettext)** (当同一个词在不同语境下有不同翻译时)

{% load i18n %}

{\# 示例: "May" 作为月份 \#}  
\<p\>{% pgettext "month name" "May" %}\</p\>

{\# 示例: "May" 作为情态动词 \#}  
\<p\>{% pgettext "modal verb" "May I help you?" %}\</p\>

**f. 特殊注意事项**

* **不要在 HTML 属性值内直接使用 trans 标签** (虽然有时能工作，但不推荐，易出错)。  
  * **错误:** \<input placeholder="{% trans 'Search' %}"\>  
  * **正确 (方法一: 使用 as):**  
    {% trans "Search" as search\_placeholder %}  
    \<input placeholder="{{ search\_placeholder }}"\>

  * **正确 (方法二: Python 中翻译):** 在视图或表单中翻译，然后传递给模板。  
* **模板过滤器干扰:** 避免在 trans 标签内直接使用过滤器。  
  * **错误:** {% trans "Page"|title %}  
  * **正确:** {% filter title %}{% trans "page" %}{% endfilter %}  
* **换行符:** trans 或 blocktrans 中的换行符会保留在 .po 文件和最终输出中。

➡️ **查看 templates/accounts/profile.html 示例代码**: [my-project/tree/main/templates/accounts/profile.html](https://github.com/F16TH/my-project/tree/main/templates/accounts/profile.html)

#### **2\. Python 代码 (.py 文件)**

导入 gettext\_lazy as \_，并使用 \_("...") 标记模型字段、表单标签、视图消息等需要翻译的字符串。

**a. 导入翻译函数**

在需要翻译的 Python 文件顶部导入：

from django.utils.translation import gettext  
from django.utils.translation import gettext\_lazy as \_  
from django.utils.translation import pgettext, pgettext\_lazy  
from django.utils.translation import ngettext, ngettext\_lazy

* gettext / \_: 立即翻译 (用于视图、表单处理等运行时)。\_ 是 gettext\_lazy 的常用别名。  
* gettext\_lazy / \_: 惰性翻译 (用于模型字段、表单字段标签、URL 名称等在 Django 加载时就需要定义，但翻译需要延迟到请求时)。**这是最常用的。**  
* pgettext / pgettext\_lazy: 带上下文的翻译。  
* ngettext / ngettext\_lazy: 复数形式翻译。

**b. 标记字符串**

```python
# models.py  
from django.db import models  
from django.utils.translation import gettext_lazy as _

class Category(models.Model):  
    name = models.CharField(_("Category Name"), max_length=100) # 字段 verbose_name  
    description = models.TextField(_("Description"), blank=True)

    class Meta:  
        verbose_name = _("Category") # 模型单数名  
        verbose_name_plural = _("Categories") # 模型复数名
```

```python
# forms.py  
from django import forms  
from django.utils.translation import gettext_lazy as _

class ContactForm(forms.Form):  
    name = forms.CharField(label=_("Your Name"), max_length=100)  
    email = forms.EmailField(label=_("Your Email"))  
    message = forms.CharField(label=_("Message"), widget=forms.Textarea, help_text=_("Please enter your message here."))
```

```python
# views.py  
from django.shortcuts import render  
from django.contrib import messages  
from django.utils.translation import gettext # 使用 gettext 进行立即翻译  
from django.utils.translation import ngettext

def my_view(request):  
    # ...  
    num_items = get_number_of_items() # 假设这个函数返回物品数量  
    if request.method == 'POST':  
        # ... 处理表单 ...  
        # 使用 gettext 翻译成功消息  
        messages.success(request, gettext("Your profile was updated successfully!"))  
    else:  
        # 使用 ngettext 处理复数  
        message = ngettext(  
            "You have %(count)d item.",  
            "You have %(count)d items.",  
            num_items  
        ) % {'count': num_items}  
        context = {'dynamic_message': message}  
    # ...  
    return render(request, 'my_template.html', context)

# urls.py (翻译 URL 名称 - 不常见，但可能)  
# from django.urls import path  
# from . import views  
# from django.utils.translation import gettext_lazy as _  
#  
# urlpatterns = [  
#     path(_('profile/'), views.profile, name='user_profile'),  
# ]
```

**c. 哪些 Python 文件需要翻译？**

通常是那些包含用户可见文本的文件：

* models.py: 字段的 verbose\_name, help\_text, 模型的 verbose\_name, verbose\_name\_plural。  
* forms.py: 字段的 label, help\_text, 错误信息。  
* views.py: 使用 messages 框架发送的消息，传递给模板的动态字符串。  
* admin.py: 列表显示的列名 (list\_display)，过滤器标题 (list\_filter) 等 (如果需要自定义)。


➡️ 查看 accounts/models.py 示例代码: [my-project/accounts/models.py](https://github.com/F16TH/my-project/tree/main/accounts/models.py)  
➡️ 查看 accounts/forms.py 示例代码: [my-projcet/accounts/forms.py](https://github.com/F16TH/my-project/tree/main/accounts/forms.py)

### **六. 生成和编译翻译文件**

#### **1\. 生成翻译文件 (.po)**

在项目根目录运行命令以扫描代码和模板，生成或更新 .po 文件。

\# 为简体中文生成/更新 .po 文件  使用--ignore=venv避免扫描到虚拟环境中的字符串
python manage.py makemessages \-l zh\_Hans \--ignore=venv

\# 为所有语言生成/更新 .po 文件  
python manage.py makemessages \-a \--ignore=venv

#### **2\. 编辑翻译文件 (.po)**

手动编辑 locale/\<lang\>/LC\_MESSAGES/django.po 文件，在 msgstr 行填入翻译。

➡️ **查看 locale/zh\_Hans/LC\_MESSAGES/django.po 示例文件**: [my-projcet/locale/zh\_Hans/LC\_MESSAGES/django.po](https://github.com/F16TH/my-project/tree/main/locale/zh_Hans/LC_MESSAGES/django.po)

#### **3\. 编译翻译文件 (.mo)**

运行命令将编辑好的 .po 文件编译成 Django 使用的 .mo 二进制文件。

python manage.py compilemessages \--ignore=venv

编译后的 .mo 文件通常不建议直接提交到版本控制中（但 .po 文件应该提交），因为它们是生成文件。

## **生产环境部署 (示例: Nginx \+ Gunicorn)**

确保服务器上已安装 gettext 工具集。

### **Nginx 配置**

关键是传递 Accept-Language 头。
```
location / {  
    \# ... 其他 proxy 设置 ...  
    proxy\_set\_header Accept-Language $http\_accept\_language; \# 传递浏览器语言偏好  
    proxy\_pass http://unix:/path/to/your/project/myproject.sock; \# 根据实际情况修改 socket 路径  
}
```

### **Gunicorn 配置**

通常不需要特殊配置，确保 Gunicorn 能加载 Django 配置即可。

\# 示例 Gunicorn 启动命令  
gunicorn myproject.wsgi:application \--bind unix:/path/to/your/project/myproject.sock ... \# 根据实际情况修改


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
