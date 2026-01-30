from django import forms
from django.contrib.auth.forms import UserCreationForm

# from captcha.fields import ReCaptchaField
# from captcha.widgets import ReCaptchaV2Checkbox
from userauths.models import User

USER_TYPE = (
    ('customer', 'Customer'),
    ('vendor', 'Vendor'),
)

class UserRegisterForm(UserCreationForm):
    full_name = forms.CharField(max_length=100, required=True, help_text='Required. Enter your full name.')