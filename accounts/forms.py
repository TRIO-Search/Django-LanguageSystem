from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'bio', 'avatar', 'website')