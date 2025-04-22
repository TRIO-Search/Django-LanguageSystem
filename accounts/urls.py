from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView

from .views import upload_document

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(template_name='registration/logged_out.html', next_page='home'), name='logout'),
    path('upload/', upload_document, name='upload_document'),
]