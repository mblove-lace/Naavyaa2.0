from django import forms
from django.contrib.auth.forms import UserCreationForm

from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from userauths.models import User

USER_TYPE = (
    ('customer', 'Customer'),
    ('vendor', 'Vendor'),
)

# Importing Djasngo's built-in UserCreationForm to leverage its password validation and user creation logic, while customizing it with our additional fields and reCAPTCHA for enhanced security.
# 
class UserRegisterForm(UserCreationForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control rounded', 'placeholder': 'Full Name'}), required=True)
    mobile= forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control rounded', 'placeholder': 'Mobile Number'}), required=True)
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control rounded', 'placeholder': 'Email Address'}), required=True)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control rounded', 'placeholder': 'Password'}), required=True)
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control rounded', 'placeholder': 'Confirm Password'}), required=True)
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())
    user_type = forms.ChoiceField(choices=USER_TYPE, widget=forms.Select(attrs={'class': 'form-control rounded'}), required=True)
    
    class Meta:
        model = User
        fields = ['full_name', 'mobile', 'email', 'password1', 'password2', 'user_type']

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control rounded', 'placeholder': 'Email Address'}), required=True)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control rounded', 'placeholder': 'Password'}), required=True)
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    class Meta:
        model = User
        fields = ['email', 'password1', 'captcha']
        
 
    