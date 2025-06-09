from django.db import models

# Create your models here.
from shortuuid.django_fields import ShortUUIDField
from userauths.models import User
from django.utils.text import slugify


NOTIFICATION_TYPE = (
    ("New Order", "New Order"),
    ("New Review", "New Review"),
)

PAYMENT_METHOD = (
    ("Cash on Delivery", "Cash on Delivery"),
    ("Online Payment", "Online Payment"),
)

PAYOUT_METHOD = (
    (")