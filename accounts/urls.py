from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout')
]