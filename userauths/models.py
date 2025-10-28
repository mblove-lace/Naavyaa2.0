from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

USER_TYPE = (
    ('Vendor', 'Vendor'),
    ('Customer', 'Customer'),
)

class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True, null=True, blank=True)
    email = models.EmailField(max_length=255, unique=True)


USERNAME_FIELD = 'email'
REQUIRED_FIELDS = ['username']


def __str__(self):
    return self.email

def save(self, *args, **kwargs):
    email_username = self.email.split('@')
    if not self.username:
        self.username = email_username
    super(User, self).save(*args, **kwargs)

class Profile (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image= models.ImageField(upload_to='images', default='default-user.jpg',null=True, blank=True)
    full_name = models.CharField(max_length=50, choices=None,null=True, blank=True)
    mobile = models.CharField(max_length=10, null=True, blank=True)
    user_Type = models.CharField(max_length=150, choices=USER_TYPE,null=True, blank=True,default=None)

def __str__(self):
    return self.user.username

def save(self, *args, **kwargs):
    if not self.full_name:
        self.full_name = self.user.username
    super(Profile, self).save(*args, **kwargs)