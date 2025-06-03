from django.db import models

# Importing the Product model from the store app.
# This is needed because the Wishlist model includes a ForeignKey to Product,
# indicating that each wishlist item is linked to a product from the store.

from store.models import Product

# Importing the User model from a custom user authentication app.
# This is required to associate users with wishlists, addresses, and notifications.

from userauths.models import User

TYPE = (
    ("New Order", "New Order"),
    ("Item Shipped", "Item Shipped"),
    ("Item Delivered", "Item Delivered"),
    ("Item Cancelled", "Item Cancelled"),
    ("Item Returned", "Item Returned"),
)

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='wishlist')

    class Meta:
        verbose_name_plural = "Wishlist"
       

    def __str__(self):
        if self.product.name:
            return self.product.name
        else:
            return "Wishlist"
        
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    full_name = models.CharField(max_length=200, null=True, blank=True,default=None)
    mobile = models.CharField(max_length=15, null=True, blank=True, default=None)
    email = models.EmailField(max_length=254, null=True, blank=True, default=None)
    country = models.CharField(max_length=100, null=True, blank=True, default=None)
    state = models.CharField(max_length=100, null=True, blank=True, default=None)
    city = models.CharField(max_length=100, null=True, blank=True, default=None)
    address = models.CharField(max_length=200,null=True, blank=True, default=None)
    zip_code = models.CharField(max_length=20, null=True, blank=True, default=None)

    class Meta:
        verbose_name_plural = "Customer Address"


    def __str__(self):
        return self.full_name
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=100, choices=TYPE, default="New Order")
    seen = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Notifications"

    def __str__(self):
        return self.type