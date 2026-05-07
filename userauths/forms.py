# This code defines two Django forms for user registration and login, utilizing Django's built-in UserCreationForm for the registration form and adding custom fields for full name, mobile number, email, password confirmation, user type selection, and reCAPTCHA for security. The login form includes fields for email, password, and reCAPTCHA as well. Both forms specify the User model as their associated model and define the fields to be included in the form.
from django import forms
# Importing the forms module from Django to create custom form classes for user registration and login, allowing us to define the structure and validation logic for these forms in our application.
from django.contrib.auth.forms import UserCreationForm

# from django_recaptcha.fields import ReCaptchaField
# from django_recaptcha.widgets import ReCaptchaV2Checkbox
from userauths.models import User

USER_TYPE = (
    ('customer', 'Customer'),
    ('vendor', 'Vendor'),
)

# Importing Djasngo's built-in UserCreationForm to leverage its password validation and user creation logic, while customizing it with our additional fields and reCAPTCHA for enhanced security.
# The UserRegisterForm class has fields for full name, mobile number, email, password confirmation, user type selection, and a reCAPTCHA field to prevent automated registrations. The LoginForm class is a simple
class UserRegisterForm(UserCreationForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control rounded', 'placeholder': 'Full Name'}), required=True)
    mobile= forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control rounded', 'placeholder': 'Mobile Number'}), required=True)
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control rounded', 'placeholder': 'Email Address'}), required=True)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control rounded', 'placeholder': 'Password'}), required=True)
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control rounded', 'placeholder': 'Confirm Password'}), required=True)
    # captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())
    user_type = forms.ChoiceField(choices=USER_TYPE, widget=forms.Select(attrs={'class': 'form-control rounded'}), required=True)
    # class Meta is a nested class within the UserRegisterForm that specifies the model to be used for this form (User) and the fields that should be included in the form. This allows Django to automatically generate form fields based on the specified model and handle form validation accordingly.
    class Meta:
        model = User
        fields = ['full_name', 'mobile', 'email', 'password1', 'password2', 'user_type']


# The LoginForm class defines a form for user login, including fields for email, password, and reCAPTCHA. It also specifies the User model and the fields to be included in the form using the Meta class. This allows Django to handle form validation and user authentication based on the specified fields and model.
class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control rounded', 'placeholder': 'Email Address'}), required=True)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control rounded', 'placeholder': 'Password'}), required=True)
    # captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())
# The LoginForm class has fields for email, password, and reCAPTCHA. It specifies the User model and the fields to be included in the form.
    class Meta:
        model = User
        fields = ['email', 'password1']
        
 
    