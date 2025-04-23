from django import forms

from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

from .models import UserDocument

from django.utils.translation import gettext_lazy as _

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label=_("Email"),  # 字段标签
        help_text=_("We'll never share your email with others.")  # 帮助文本
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': _("Username"),
            'password1': _("Password"),
            'password2': _("Password Confirmation")
        }
        help_texts = {
            'username': _("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."),
        }
        error_messages = {
            'username': {
                'unique': _("This username is already taken."),
                'invalid': _("Contains invalid characters.")
            },
            'password2': {
                'password_mismatch': _("The two password fields didn't match.")
            }
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'bio', 'avatar', 'website')
        labels = {
            'bio': _("Biography"),
            'avatar': _("Profile Picture"),
            'website': _("Website URL")
        }
        help_texts = {
            'website': _("Your personal or professional website (e.g. https://example.com)"),
            'bio': _("Tell others about yourself")
        }

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = UserDocument
        fields = ['document', 'title']
        labels = {
            'document': _("File"),
            'title': _("Document Title")
        }
        help_texts = {
            'document': _("Allowed formats: PDF, DOCX, TXT (Max 10MB)"),
            'title': _("Give your document a descriptive name")
        }
        error_messages = {
            'document': {
                'invalid': _("Invalid file format"),
                'missing': _("No file was selected")
            }
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _("My Document")  # 输入框占位符
            }),
            'document': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.docx,.txt'
            })
        }