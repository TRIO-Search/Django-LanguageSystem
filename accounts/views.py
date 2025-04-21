from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, ProfileForm
from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True #已登录直接跳转

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        print("表单数据：", request.POST) #调试日志相关
        if form.is_valid():
            print("表单验证通过")
            user = form.save()
            login(request, user)
            print("用户已创建并登录")
            return redirect('profile')
        else:
            print("表单错误：", form.errors)
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {
        'form': form
    })

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES,  instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'form': form
    })


