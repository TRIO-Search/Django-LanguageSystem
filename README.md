# **Django i18n 语言切换功能开发文档**

## **目录**

* [功能概述](#功能概述)  
* [开发环境配置](#开发环境配置)  
* [核心实现步骤](#核心实现步骤)  
* [生产环境部署](#生产环境部署-示例-nginx--gunicorn)  
* [维护指南](#维护指南)  
* [常见问题排查](#常见问题排查)

## **功能概述**

实现多语言切换系统，支持：

* 中英文双语切换  
* 用户个人语言偏好保存  
* 生产环境无缝部署

## **开发环境配置**

### **系统依赖**

Ubuntu/WSL  
GNU gettext 工具集，这是Django国际化(i18n)的底层依赖，若项目要部署在服务器上则需要在服务器也下载此工具集 

使用`sudo apt-get install gettext`下载gettext

示例Django项目所用版本为5.2 (请根据你的项目调整)  
`python -m pip install django==5.2`

### **项目结构（以本项目为示例）**
```
my-project/               # 项目根目录
├── locale/               # 翻译文件目录  
│   └── zh_Hans/          # 简体中文 (或其他语言代码, 如 en)  
│       └── LC_MESSAGES/  
│           ├── django.po # 翻译模板文件  
│           └── django.mo # 编译后的翻译文件  
├── accounts/             # 示例应用  
│   ├── models.py  
│   ├── views.py  
│   └── urls.py  
│   └── forms.py  
├── templates/            # HTML 模板目录  
│   ├── base.html         # 基础模板  
│   └── accounts/  
│       └── profile.html  # 示例模板  
├── myproject/            # Django 项目配置目录  
│   └── settings/
|       ├── dev.py        # 开发环境额外配置
|       ├── prod.py       # 生产环境额外配置
│       └── base.py       # 基础配置（注意：如果你未对开发与生产环境进行分别配置，那么配置文件一般就是settings.py）
├── manage.py  
└── ... (其他文件)
```
## **核心实现步骤**

### **一. 基础配置 (myproject/settings/base.py)**

进行语言切换开发必须的基础配置，包括启用 `i18n`、设置`默认语言`、定义 `LOCALE_PATHS` 和添加 `LocaleMiddleware`。

下为示例，注释内容为功能说明。

或可查看本项目代码➡️ **查看 myproject/settings/base.py 代码**: [my-project/myproject/settings/base.py](https://github.com/F16TH/my-project/tree/main/myproject/settings/base.py)

```python
# settings.py 或 settings/base.py，如果你没对生产与开发环境配置做过区分一般是settings.py
# 请确保你的配置文件有以下内容

import os  
from django.utils.translation import gettext_lazy as _ # 翻译所需

# BASE_DIR指向项目根目录 (根据你的项目结构调整)  
BASE_DIR = Path(__file__).resolve().parent.parent.parent     #.parent用于回溯到上级目录

# 启用 i18n 和 l10n  
USE_I18N = True # USE_I18N 设置为 True 启用 Django 的国际化功能，允许你使用翻译系统来处理多语言内容。
USE_L10N = True # 通常与 USE_I18N 一起启用，用于格式化日期、数字等

# 默认语言  
LANGUAGE_CODE = 'zh-hans' # 设置项目默认语言，可确保所有未翻译的字符串使用默认语言显示，避免出现未翻译的占位符。

# 可用语言列表  
LANGUAGES = [  
    ('en', _('English')),         # 英文  
    ('zh-hans', _('Simplified Chinese')), # 简体中文  
    # ('ja', _('Japanese')), # 可以添加更多语言  
]    #后续编译翻译文件的 makemessages 命令会根据 LANGUAGES 列表生成相应的 .po 文件。

# 翻译文件路径  
LOCALE_PATHS = [  
    os.path.join(BASE_DIR, 'locale'), # 指向包含各语言翻译文件的 'locale' 目录，集中存放翻译文件便于维护
]

# 生产环境下Django的挂载点，将你django挂载到的子目录写入这一项，比如挂载到demo.com/user，则写入TARGET_URL = 'user'
TARGET_URL = ''

# 中间件配置  
MIDDLEWARE = [  
    # ... 其他中间件  
    'django.contrib.sessions.middleware.SessionMiddleware', # Session 中间件，必须在 LocaleMiddleware 之前，因为语言设置依赖于会话数据
    'django.middleware.locale.LocaleMiddleware',          # 核心：处理语言切换的中间件，必须在 SessionMiddleware 之后，CommonMiddleware 之前  
    'django.middleware.common.CommonMiddleware',  
    # ... 其他中间件  
]
```


### **二. 语言切换视图**

#### **为什么要有`set_language`视图函数？** 

`set_language` 视图在 Django 项目中扮演着关键角色，用于处理用户选择的语言切换。其主要作用包括：
1. 获取并验证用户选择的语言代码。
2. 设置会话和 Cookie 中的语言，确保语言设置持久化。
3. 激活当前语言，确保当前请求中的翻译文本使用该语言。
4. 重定向用户，将用户重定向到指定的页面，并应用新的语言设置。

如果不设置 `set_language` 视图，项目将无法支持动态语言切换，用户语言设置无法持久化，用户体验会显著下降，并且可能引入安全风险。

**Django官方提供了`set_language`视图函数，本项目也是使用官方的`set_language`，在 [三. 语言切换 URL 配置 (myproject/urls.py)](#三-语言切换-url-配置-myprojecturlspy) 之中会告诉你如何将 URL 链接到官方的`set_language`**

**以下代码只是作为示例参考，更推荐使用官方的`set_language`视图函数**

```python
# accounts/views.py (或项目内任何合适的位置)

from django.http import HttpResponseRedirect  
from django.conf import settings  
from django.views.decorators.http import require_POST  
from django.utils.translation import activate

@require_POST # 确保只接受 POST 请求  
def set_language(request):
    lang_code = request.POST.get('language')
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or '/'
    
    if lang_code in dict(settings.LANGUAGES).keys():
        request.session['django_language'] = lang_code 
        activate(lang_code)
        
        response = HttpResponseRedirect(next_url)
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME, 
            lang_code,
            max_age=365*24*60*60,
            secure=request.is_secure(),
            httponly=True
        )
        return response
    return HttpResponseRedirect(next_url)
```
#### **函数功能讲解**
```
lang_code = request.POST.get('language')
```
* 作用：从 POST 请求中获取用户选择的语言代码（例如 `en` 或 `zh-hans`）。
* 来源：通常来自前端表单中的 `<input type="hidden" name="language" value="en">` 或 `<select name="language">`。
```
next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or '/'
```
* 作用：确定用户在语言切换后应该重定向到哪个页面。
* 优先级：
1. `request.POST.get('next')`：从 POST 数据中获取 `next` 参数。
2. `request.META.get('HTTP_REFERER')`：如果没有 `next` 参数，则使用 `HTTP Referer` 头。
3. `'/'`：如果以上都没有，则重定向到根路径。
```
if lang_code in dict(settings.LANGUAGES).keys():
```
* 作用：检查用户选择的语言代码是否在 settings.LANGUAGES 中定义。
* 安全性：确保用户只能选择项目支持的语言，防止无效或恶意的语言代码。
```
request.session['django_language'] = lang_code
```
* 作用：将用户选择的语言代码存储在会话中，以便在后续请求中使用。
* 持久性：会话数据通常存储在服务器端，用户在会话期间保持选择的语言。
```
activate(lang_code)
```
* 作用：立即激活用户选择的语言，确保当前请求中的翻译文本使用该语言。
* 即时生效：在当前请求中立即生效，不需要等待会话保存。
```
response = HttpResponseRedirect(next_url)
```
* 作用：创建一个重定向响应，将用户重定向到 `next_url`。
* 重定向：用户在语言切换后会看到相应语言的页面。
```
response.set_cookie(
    settings.LANGUAGE_COOKIE_NAME,  # 默认为 'django_language'
    lang_code,
    max_age=365*24*60*60,  # 一年
    secure=request.is_secure(),
    httponly=True
)
```
* 作用：在响应中设置语言 Cookie，以便在用户后续访问时保持语言选择。
* 参数说明：
    `settings.LANGUAGE_COOKIE_NAME`：Cookie 名称，默认为 'django_language'。
    `lang_code`：用户选择的语言代码。
    `max_age`：Cookie 的有效期，这里设置为一年。
    `secure`：如果请求是 HTTPS，则设置 Cookie 为安全 Cookie。
    `httponly`：防止 JavaScript 访问 Cookie，提高安全性。
```
return response
```
* 作用：返回重定向响应，将用户重定向到指定的页面，并设置语言 Cookie。
```
return HttpResponseRedirect(next_url)
```
* 作用：如果用户选择的语言代码无效，则直接重定向到 `next_url`，不进行任何语言设置。
* 容错性：确保即使用户提交了无效的语言代码，也不会导致错误，而是安全地重定向。

### **三. 语言切换 URL 配置 (myproject/urls.py)**

#### **为什么将 `set_language` 视图函数连接到特定的 `URL` 路径。**
1. 前端表单提交目标：
* 提交地址：前端表单需要一个明确的 URL 来提交语言选择数据。
* 一致性：通过固定的 URL 路径，确保前端和后端之间的通信一致。
2. 路由管理：
* URL 映射：Django 的 URL 路由系统负责将请求 URL 映射到相应的视图函数。
* 可维护性：通过 URL 路由，可以方便地管理和修改 URL 结构，而不会影响视图逻辑。
3. 安全性：
* CSRF 保护：Django 的 CSRF 保护机制依赖于明确的 URL 路径来验证请求的合法性。
* 权限控制：可以通过 URL 路径进行权限控制，确保只有授权用户才能进行语言切换。
4. 用户体验：
* 一致的用户交互：用户通过点击或选择语言选项来触发语言切换，前端表单需要一个明确的提交地址。
* 即时反馈：用户选择语言后，立即重定向到相应的页面，提供即时的反馈。
5. 开发和调试：
* 清晰的接口：通过 URL 路径，开发人员可以清晰地了解哪些 URL 路径对应哪些功能。
* 调试方便：在开发和调试过程中，可以通过 URL 路径快速定位和解决问题。

以下为代码示例。
或者可查看本项目代码➡️ 查看 myproject/urls.py 代码: [my-project/myproject/urls.py](https://github.com/F16TH/my-project/tree/main/myproject/urls.py)  

在项目的主 urls.py 或应用的 urls.py 中添加路径：

 **(除非语言切换功能只与应用有关，否则更推荐在项目的主 urls.py 中添加路径)**

```python
# myproject/urls.py (主 URL 配置)  
from django.contrib import admin  
from django.urls import path, include  
from django.conf import settings

urlpatterns = [  
    path('admin/', admin.site.urls),  
    # ... 其他应用的 URL  
    path(settings.TARGET_URL + '/i18n/',include('django.conf.urls.i18n')), # 直接在主 urls.py 定义  
]

```

#### **对`path(settings.TARGET_URL + '/i18n/',include('django.conf.urls.i18n'))`的一些说明**

* `settings.TARGET_URL`是你在项目的配置文件中写入的，Django在生产环境下的挂载点，如果没有这个，在生产环境下Django无法获得完整的URL，会导致Django无法将请求URL路由到`set_language`
* `'/i18n/'`使得该`path`路由到`settings.TARGET_URL/i18n/setlang`防止`settings.TARGET_URL`被其他视图占用导致的冲突使得语言切换功能无法工作
* `django.conf.urls.i18n` 是 Django 内置的一个模块，专门用于处理国际化（i18n）相关的功能，比如语言切换。使用它的好处是无需自己编写语言切换的视图和 URL 模式，直接复用 Django 的内置实现即可。
    * 核心功能：
        * `django.conf.urls.i18n` 提供了一个默认的 URL 模式 `/i18n/setlang/`，用于处理语言切换请求。
        * 它会调用 Django 内置的视图 `django.views.i18n.set_language` 来实现语言切换逻辑。


### **四. 模板语言切换控件 (templates/base.html)**

在 HTML 基础模板中添加一个表单，允许用户选择语言。该表单会提交到 `set_language` 视图。

以下为示例。或者可查看本项目代码➡️ **查看 templates/base.html 代码**: [my-project/templates/base.html](https://github.com/F16TH/my-project/tree/main/templates/base.html#L35-L47)

```html
{# templates/base.html中的控件，可将此代码插入到你需要的位置 #}  
{% load i18n %} {# 加载 i18n 标签库，这个和翻译相关，最好是放在文件顶以便于优先加载 #}

<form action="{% url 'set_language' %}" method="post">  {# 切换语言的控件 #}
    {% csrf_token %}
    <input name="next" type="hidden" value="{{ request.get_full_path }}">
    <select name="language" onchange="this.form.submit()">
        {% get_available_languages as LANGUAGES %}
        {% get_current_language as CURRENT_LANG %}
        {% for code, name in LANGUAGES %}
        <option value="{{ code }}" {% if code == CURRENT_LANG %}selected{% endif %}>
            {{ name }}
        </option>
        {% endfor %}
    </select>
</form>
```
#### **控件代码讲解**
```
<form action="{% url 'set_language' %}" method="post">
```
* `action` 属性：
    `{% url 'set_language' %}`：使用 Django 的 `{% url %}` 模板标签生成 `set_language` 视图的 URL。
* `method` 属性：
    `post`：使用 POST 方法提交表单数据，确保安全性。
```
{% csrf_token %}
```
* 作用：
    生成一个 CSRF 令牌，防止跨站请求伪造攻击。
    Django 的 CSRF 中间件会验证这个令牌，确保请求是合法的。
```
<input name="next" type="hidden" value="{{ request.get_full_path }}">
```
* `name` 属性：`next`用于存储用户当前的 URL 路径。
* `type` 属性：`hidden`隐藏字段，用户不可见。
* `value` 属性：`{{ request.get_full_path }}`使用 Django 的 `request.get_full_path` 获取当前请求的路径（包括查询参数），确保语言切换后重定向回当前页面。
```
<select name="language" onchange="this.form.submit()">
```
* `name` 属性：`language`用于存储用户选择的语言代码。
* `onchange` 属性：`this.form.submit()`当用户选择不同的语言时，自动提交表单。
```
{% get_available_languages as LANGUAGES %}
```
* 作用：
    1. 使用 Django 的 `{% get_available_languages %}` 模板标签获取所有可用的语言列表。
    2. `LANGUAGES` 是一个包含语言代码和名称的列表，在前面对 Django 的基础配置中已经设置好了。
```
{% get_current_language as CURRENT_LANG %}
```
* 作用：
    1. 使用 Django 的 `{% get_current_language %}` 模板标签获取当前的语言代码。
    2. `CURRENT_LANG` 是当前选择的语言代码。
```
{% for code, name in LANGUAGES %}
<option value="{{ code }}" {% if code == CURRENT_LANG %}selected{% endif %}>
    {{ name }}
</option>
{% endfor %}
```
* 循环：
    遍历 LANGUAGES 列表中的每个语言项。
* 选项标签 (`<option>`)
    * `value` 属性：
        `{{ code }}`：语言代码（例如 `en` 或 `zh-hans`）。
    * `selected` 属性：
        `{% if code == CURRENT_LANG %}selected{% endif %}`：如果当前语言代码与选项中的语言代码匹配，则选中该选项。
    * 显示文本：
        `{{ name }}`：语言名称（例如 `English` 或 `简体中文`）。
      
#### **工作流程**
1. 用户选择语言：
    用户在下拉菜单中选择一种语言（例如 `简体中文`）。
2. 自动提交表单：
    选择语言后，`onchange="this.form.submit()"` 触发表单的自动提交。
3. 发送 POST 请求：
    表单数据（包括 `language` 和 `next`）通过 POST 方法发送到 `set_language` 视图。
4. 处理请求：
    `set_language` 视图处理请求，验证语言代码，设置会话和 Cookie 中的语言，并重定向用户到 `next` 参数指定的 URL。
5. 重定向：
    用户被重定向回当前页面，并应用新的语言设置。

### **五. 标记需要翻译的字符串**

#### **1. HTML 模板 (.html 文件)**

使用 `{% load i18n %}` 加载标签库，并使用 `{% trans "..." %}` 或 `{% blocktrans %} ... {% endblocktrans %}` 标记需要翻译的文本（其中...替换为需要标记的字符串）。具体操作如下

**重要:** 在每个需要翻译的模板文件顶部添加 `{% load i18n %}`以确保翻译标签可被正常识别，否则会报错。

**a. 简单翻译 (`trans`)**
```
{% load i18n %}

<h1>My Profile</h1>    <!-- 一般未被标记的字符串 -->
<h1>{% trans "My Profile" %}</h1>  <!-- 使用{% trans "..." %}标记需要翻译的字符串 -->

<p>{% trans "This text will be translated." %}</p>  
<button type="submit">{% trans "Save Changes" %}</button>
```
**b. 带变量的翻译 (`trans` 或 `blocktrans`)**
```
{% load i18n %}

{# 使用 trans 标签 (简单变量) #}  
<p>{% trans "Welcome back," %} {{ user.username }}!</p>

{# 使用 blocktrans 标签 (更清晰，尤其是有多个变量或 HTML 时) #}  
{% blocktrans with username=user.username %}Hello {{ username }}, how are you?{% endblocktrans %}

{# blocktrans 示例：包含 HTML #}  
{% blocktrans %}You can <a href="/profile/">edit your profile</a>.{% endblocktrans %}
```
**c. 块翻译 (`blocktrans`)** (用于多行文本或包含模板标签/过滤器)
```
{% load i18n %}

{# 多行文本 #}  
{% blocktrans %}  
This is the first line.  
This is the second line.  
{% endblocktrans %}

{# 包含变量和过滤器 #}  
{% blocktrans with user_count=users|length %}  
There are {{ user_count }} active users.  
{% endblocktrans %}
```
**d. 复数形式 (`blocktrans` 与 `plural`)**
```
{% load i18n %}

{% blocktrans count counter=documents.count %}  
You have 1 document.  
{% plural %}  
You have {{ counter }} documents.  
{% endblocktrans %}

{% blocktrans with amount=cart.total count items_count=cart.items.count %}  
Your cart has {{ items_count }} item. Total: ${{ amount }}.  
{% plural %}  
Your cart has {{ items_count }} items. Total: ${{ amount }}.  
{% endblocktrans %}
```
**e. 添加翻译上下文 (`pgettext`)** (当同一个词在不同语境下有不同翻译时)
```
{% load i18n %}

{# 示例: "May" 作为月份 #}  
<p>{% pgettext "month name" "May" %}</p>

{# 示例: "May" 作为情态动词 #}  
<p>{% pgettext "modal verb" "May I help you?" %}</p>
```
**f. 特殊注意事项**

* **不要在 HTML 属性值内直接使用 `trans` 标签**
  * **原因：**
      * 如果翻译字符串中包含特殊字符（如 `"` 或 `'`），可能会破坏 HTML 属性的结构，这会导致 HTML 解析错误。
      * 在 HTML 属性值中直接使用 `{% trans %}` 标签，可能会使模板代码变得复杂且难以阅读。
  * **错误:** `<input placeholder="{% trans 'Search' %}">  `
  * **正确 (方法一: 使用 as):**
  * ```
    {% trans "Search" as search_placeholder %}  
    <input placeholder="{{ search_placeholder }}">
    ```
  * **正确 (方法二: Python 中翻译):** 在视图或表单中翻译，然后传递给模板。  
* **模板过滤器干扰:** 避免在 `trans` 标签内直接使用过滤器，这会导致语法错误。  
  * **错误:** `{% trans "Page"|title %}`  
  * **正确:** `{% filter title %}{% trans "page" %}{% endfilter %} ` 
* **换行符:** `trans` 或 `blocktrans` 中的换行符会保留在 .po 文件和最终输出中。

➡️ **查看 templates/accounts/profile.html 示例代码**: [my-project/tree/main/templates/accounts/profile.html](https://github.com/F16TH/my-project/tree/main/templates/accounts/profile.html)

#### **2. Python 代码 (.py 文件)**

使用`from django.utils.translation import gettext_lazy as _`导入翻译标签，并使用 `_("...")` 标记模型字段、表单标签、视图消息等需要翻译的字符串。

**a. 导入翻译函数**

在需要翻译的 Python 文件顶部导入：
```
from django.utils.translation import gettext  
from django.utils.translation import gettext_lazy as _  
from django.utils.translation import pgettext, pgettext_lazy  
from django.utils.translation import ngettext, ngettext_lazy
```
* `gettext / _`: 立即翻译 (用于视图、表单处理等运行时)。_ 是 gettext_lazy 的常用别名。  
* `gettext_lazy / _`: 惰性翻译 (用于模型字段、表单字段标签、URL 名称等在 Django 加载时就需要定义，但翻译需要延迟到请求时)。**这是最常用的，如无其他特殊需要，只导入这个也行。**  
* `pgettext / pgettext_lazy`: 带上下文的翻译。  
* `ngettext / ngettext_lazy`: 复数形式翻译。

**b. 标记字符串**

以下是标记示例，若需要可用的代码请查看本项目内代码

➡️ 查看 accounts/models.py 示例代码: [my-project/accounts/models.py](https://github.com/F16TH/my-project/tree/main/accounts/models.py)  

➡️ 查看 accounts/forms.py 示例代码: [my-projcet/accounts/forms.py](https://github.com/F16TH/my-project/tree/main/accounts/forms.py)

➡️ 查看 accounts/viewss.py 示例代码: [my-projcet/accounts/views.py](https://github.com/F16TH/my-project/tree/main/accounts/views.py)

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

* `models.py`: 字段的 `verbose_name`, `help_text`, 模型的 `verbose_name`, `verbose_name_plural`。  
* `forms.py`: 字段的 `label`, `help_text`, `错误信息`。  
* `views.py`: 使用 `messages` 框架发送的消息，传递给模板的动态字符串。  
* `admin.py`: 列表显示的列名 `(list_display)`，过滤器标题 `(list_filter)` 等 (如果需要自定义)。


### **六. 生成和编译翻译文件**

#### **1. 生成翻译文件 (.po)**

在项目根目录运行命令以扫描代码和模板，生成或更新 .po 文件。

##### **为简体中文生成/更新 .po 文件**  
在 Django 5.2 中，`makemessages` 命令会扫描整个项目（包括 Django 内置代码和第三方库），因此可能会出现未标记的字符串。

使用`--ignore="venv/*"`忽略虚拟环境中的字符串，否则会使翻译文件带有虚拟环境字符串。

`python manage.py makemessages -l zh_Hans --ignore="venv/*"`

##### **为所有语言生成/更新 .po 文件**  
`python manage.py makemessages -a --ignore="venv/*"`

#### **2. 编辑翻译文件 (.po)**

手动编辑 `locale/<lang>/LC_MESSAGES/django.po` 文件，在 `msgstr` 行填入翻译。

可查看本项目代码翻译文件格式作为参考

➡️ **查看 locale/zh_Hans/LC_MESSAGES/django.po 示例文件**: [my-projcet/locale/zh_Hans/LC_MESSAGES/django.po](https://github.com/F16TH/my-project/tree/main/locale/zh_Hans/LC_MESSAGES/django.po)

#### **3. 编译翻译文件 (.mo)**

运行命令将编辑好的 .po 文件编译成 Django 使用的 .mo 二进制文件。

`python manage.py compilemessages `

编译后的 .mo 文件通常不建议直接提交到版本控制中（但 .po 文件应该提交），因为它们是生成文件。

## **生产环境部署 (示例: Nginx + Gunicorn)**

确保服务器上已安装 gettext 工具集。
`sudo apt-get install gettext`

### **Nginx 配置**

关键是传递 `Accept-Language` 头，配置这个是为了确保 Django 能够正确地接收到客户端的首选语言信息，从而能够根据用户的浏览器设置自动切换或推荐语言，让 Django 的语言检测和切换逻辑正常工作
```
location / {  
    # ... 其他 proxy 设置 ...  
    proxy_set_header Accept-Language $http_accept_language; # 传递浏览器语言偏好
    proxy_pass http://unix:/path/to/your/project/myproject.sock; # 根据实际情况修改 socket 路径  
}
```
### **Gunicorn 配置**

通常不需要特殊配置，确保 Gunicorn 能加载 Django 配置即可。

在配置好 Nginx 和 Gunicorn 之后将二者重启应用即可。
## **维护指南**

* **定期更新翻译:** 使用`django-admin makemessages -l zh_Hans --ignore="venv/*" --no-obsolete`增量更新翻译文件（`--no-obsolete`参数会自动清理 .op 文件中不再使用的翻译条目）再用`python manage.py compilemessages `编译。  
* **代码审查:** 检查翻译标记的使用。  
* **测试:** 在不同语言下测试。  
* **备份:** 备份 locale 目录 (尤其是 .po 文件)。

## **常见问题排查**

* **翻译不生效:** 检查 `settings.py`, `MIDDLEWARE`, `LOCALE_PATHS`, .po 文件编辑和 .mo 文件编译，重启服务器，清缓存/Cookie。  
* **makemessages 找不到字符串:** 检查标记是否正确，命令运行目录，`--ignore` 参数。  
* **.po 文件语法错误:** 使用 `msgfmt -c` 检查。  
* **部分内容未翻译:** 检查是否所有相关文本都已标记。
