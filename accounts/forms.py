from django import forms

from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

from .models import UserDocument

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'bio', 'avatar', 'website')

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = UserDocument
        fields = ['document', 'title']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'document': forms.FileInput(attrs={'class': 'form-control'})
        }