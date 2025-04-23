from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _  #翻译相关
from .forms import RegisterForm, ProfileForm
from django.contrib.auth.views import LoginView

from .models import UserDocument
from .forms import DocumentUploadForm

from django.views.decorators.http import require_POST
from django.utils.translation import activate
from django.conf import settings
from django.http import HttpResponseRedirect

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def form_invalid(self, form):
        messages.error(self.request, _("Invalid username or password"))  # 登录错误提示
        return super().form_invalid(form)

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        print(_("Form data:"), request.POST)  # 日志标记
        if form.is_valid():
            print(_("Form validation passed"))
            user = form.save()
            login(request, user)
            messages.success(request, _("Registration successful!"))  # 注册成功提示
            print(_("User created and logged in"))
            return redirect('profile')
        else:
            print(_("Form errors:"), form.errors)
            messages.error(request, _("Please correct the errors below")) 
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Profile updated successfully"))  # 资料更新提示
            return redirect('profile')
        else:
            messages.warning(request, _("Failed to update profile")) 
    else:
        form = ProfileForm(instance=request.user)
    
    documents = UserDocument.objects.filter(owner=request.user).order_by('-uploaded_at')
    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'documents': documents,
        'form': form,
    })

@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.owner = request.user
            doc.save()
            messages.success(request, _("Document uploaded successfully"))  # 上传成功提示
            return redirect('profile')
        else:
            messages.error(request, _("File upload failed. Please check the format")) 
    else:
        form = DocumentUploadForm()
    return render(request, 'accounts/upload.html', {'form': form})

def test_controls(request):
    messages.info(request, _("This is a test page for UI controls"))  # 测试页说明
    return render(request, 'accounts/test_controls.html')

@require_POST
def set_language(request):
    lang_code = request.POST.get('language')
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or '/'
    
    if lang_code in dict(settings.LANGUAGES).keys():
        # 关键修正：使用实际的session键名 'django_language'
        request.session['django_language'] = lang_code  # 改为直接使用字符串
        activate(lang_code)
        
        response = HttpResponseRedirect(next_url)
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,  # 这个常量是存在的（默认值也是'django_language'）
            lang_code,
            max_age=365*24*60*60,
            secure=request.is_secure(),
            httponly=True
        )
        return response
    return HttpResponseRedirect(next_url)