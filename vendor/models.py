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
    ("Razorpay", "Razorpay"),
    ("Cash on Delivery", "Cash on Delivery"),
)

TYPE= (
    ("New Order", "New Order"),
    ("Item Shipped", "Item Shipped"),
    ("Item Delivered", "Item Delivered"),
)



class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name='vendor')
    image = models.ImageField(upload_to='shop-image.jpg', blank=True)
    store_name = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    vendor_id = ShortUUIDField(unique=True,length=6, max_length=32, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ',)
    slug = models.SlugField( blank=True, null=True, )
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        
        return str(self.store_name)

    def save(self, *args, **kwargs):
        if self.slug == '' or self.slug is None:
            self.slug = slugify(self.store_name)
        super(Vendor,self).save(*args, **kwargs)

   
class Payout(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)
    item = models.ForeignKey("store.OrderItem", on_delete=models.SET_NULL, null=True, related_name='payouts')
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    payout_id = ShortUUIDField(unique=True, length=6, max_length=32, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return  str(self.vendor)
    
    class Meta:
        ordering = ['-date']


class BankAccount(models.Model):
    vendor = models.OneToOneField(Vendor, on_delete=models.SET_NULL, null=True)
    account_type = models.CharField(max_length=50, choices= PAYOUT_METHOD, null=True, blank=True)
    account_number = models.CharField(max_length=200)
    account_holder_name = models.CharField(max_length=200)
    bank_name = models.CharField(max_length=200, null=True, blank=True)
    razorpay_account_id = models.CharField(max_length=200, null=True, blank=True)
    ifsc_code = models.CharField(max_length=20, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Bank Accounts"
        ordering = ['-date']

    def __str__(self):
        return self.bank_account
    
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vendor_notification", null=True)
    type = models.CharField(max_length=100, choices=NOTIFICATION_TYPE, default="New Order")
    order = models.ForeignKey("store.OrderItem", on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    seen = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Notifications"
    

    def __str__(self):
        return self.type