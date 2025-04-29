#  base module for Django's Object-Relational Mapping (ORM).
# What is ORM?
# Object-Relational Mapping (ORM) is a programming technique that allows developers to interact with a database using an object-oriented paradigm instead of writing raw SQL queries.
# ORMs map database tables to Python (or other language) classes, making it easier to work with data as objects.

from django.db import models
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Create your models here.
# shortuuid_fields is a Django package that provides ShortUUID fields for Django models, allowing you to use shorter, URL-friendly UUIDs instead of the default long UUIDs.
# ShortUUID is a Python library that generates concise, unambiguous, and URL-safe UUIDs.
# What is UUID? A UUID is a 128-bit number used to uniquely identify information in computer systems. It's typically represented as a 36-character string with a specific format:
# Copy123e4567-e89b-12d3-a456-426614174000

from shortuuid.django_fields import ShortUUIDField

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# timezone module from Django's django.utils is used for working with time zone-aware datetime objects and handling time zone-related operations.
# It provides functions and classes to manage time zones, including converting naive datetime objects to aware ones and vice versa.
# The timezone.now() function returns the current time in the UTC time zone, but it returns it as a timezone-aware datetime (i.e., it includes information about the time zone).
from django.utils import timezone

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# he slugify function converts a string into a slug — a URL-friendly version of a string. It typically: 1. Converts to lowercase. 2.Replaces spaces and special characters with hyphens. 
# 3. Removes characters that aren't alphanumerics or hyphens
from django.utils.text import slugify

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CKEditor is a rich text editor — it lets users write and format text like in Microsoft Word or Google Docs. 
# For example, they can:
#   Make text bold/italic/underlined
# Add headings, images, and links
# Create bullet points, tables, etc.

from django_ckeditor_5.fields import CKEditor5Field

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# This imports the 'models' from your userauths and vendor 'modules' and gives them aliases (user_models and vendor_models respectively).
# It allows you to refer to the models using the aliases instead of the full path, making the code cleaner and easier to read.
# For example, instead of writing userauths.models.User, you can just write user_models.User.

from userauths import models as user_models

import shortuuid



# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#  it's a tuple of tuples — and it's commonly used in Django model field choices.
# Each inner tuple represents a choice for a field in a Django model. 
# The first element of each inner tuple is the actual value to be set in the database, and the second element is the human-readable name for that value.
# These are Django choice field tuples that define options for dropdown/selection fields in your models.

STATUS = (
    ("Published", "Published"),
    ("Draft", "Draft"),
    ("Deleted", "Deleted"),
)

PAYMENT_STATUS = (
    ("Paid", "Paid"),
    ("Processing", "Processing"),
    ("Failed", "Failed"),
    ("Cancelled", "Cancelled"),
)

PAYMENT_METHOD = (
    ("Razorpay", "Razorpay"),
    ('Cash on Delievry', 'Cash on Delievry'),
)

ORDER_STATUS = (
    ("Pending", "Pending"),
    ("Processing", "Processing"),
    ("Shipped", "Shipped"),
    ("Delivered", "Delivered"),
    ("Cancelled", "Cancelled"),
)
SHIPPING_SERVICE = (
    ("BlueDart", "BlueDart"),
    ("DTDC", "DTDC"),
    ("Delhivery", "Delhivery"),
    ("India Post", "India Post"),
)

RATING = (
    (1,"★☆☆☆☆"),
    (2,"★★☆☆☆"),
    (3, "★★★☆☆"),
    (4, "★★★★☆"),
    (5, "★★★★★"),
)
class Category(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="image", null=True, blank=True)
    # slug = a way to identify 
    slug = models.SlugField( unique=True, null=True, blank=True) 

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["title"]

class Product(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="image", null=True, blank=True, default="product.jpg")
    description = CKEditor5Field('Text', config_name='extends')

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True,verbose_name="Sale Price")
    regular_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True, verbose_name="Regular Price")

    stock = models.PositiveIntegerField(default=0, null=True, blank=True)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True,verbose_name="Shipping Cost")

    status = models.CharField(max_length=50, choices=STATUS, default="Published")
    featured = models.BooleanField(default=False, verbose_name="Featured Product")

    vendor = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True, blank=True)
    
    sku = ShortUUIDField(unique=True, length=5, max_length= 50, prefix='SKU-', alphabet="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    slug = models.SlugField( unique=True, null=True, blank=True)

    date = models.DateTimeField(default=timezone.now)
    




    class Meta:
        ordering = ["-id"]
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) + "-" + str(shortuuid.uuid().lower()[:2])

        super(Product, self).save(*args, **kwargs)


class Variant (models.Model):
        
        product =models.ForeignKey(Product, on_delete=models.CASCADE,null=True)
        name = models.CharField(max_length=1000, verbose_name="Variant Name", null=True, blank=True)

        def items(self):
            return VariantItem.objects.filter(variant=self)
        
        def __str__(self):
            return self.name
        
class VariantItem(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name="variant_items",)
    title = models.CharField(max_length=1000, verbose_name="Item Title", null=True, blank=True)
    content = models.CharField(max_length=1000, verbose_name="Item Content", null=True, blank=True)

    def __str__(self):
        return self.variant.name
    

class Gallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True)
    image = models.ImageField(upload_to="images", default="gallery.jpg",null=True, blank=True)
    gallery_id = ShortUUIDField(length=5, max_length= 10, prefix='G-', alphabet="0123456789")

    def __str__(self):
        return f"{self.product.name} - images"
    

class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True, blank=True)
    qty = models.PositiveIntegerField(default=1, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    cart_id = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cart_id} - {self.product.name}"
    

class Coupon(models.Model):
    vendor = models.ForeignKey(user_models.User, on_delete=models.SET_NULL,null=True)
    code = models.CharField(max_length=100, unique=True)
    discount = models.IntegerField(default=1)
    

    def __str__(self):
        return self.code
    
class Order(models.Model):
   vendors = models.ManyToManyField(user_models.User,blank=True)
   customer = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True, blank=True, related_name="customer")
   subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00 )
   discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
   total = models.DecimalField(default = 0.0,max_digits=10, decimal_places=2)
   payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS, default="Processing")
   payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD, default="Razorpay", null=True, blank=True)
   order_status = models.CharField(max_length=100, choices=ORDER_STATUS, default="Pending")
#    address = models.ForeignKey("customer.Address", on_delete=models.SET_NULL, null=True)
   coupons = models.ManyToManyField(Coupon, blank=True)
   order_id = ShortUUIDField(length=5, max_length= 10, prefix='O-', alphabet="0123456789")
   payment_id = models.CharField(max_length=1000, null=True, blank=True)
   date = models.DateTimeField(default=timezone.now)
   
   class Meta:
        verbose_name_plural = "Order"
        ordering = ["date"]
        
   def __str__(self):
        return self.order_id
   
   def __str__(self):
        return OrderItem.objects.filter(order=self)
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_status = models.CharField(max_length=100, choices=SHIPPING_SERVICE, default="Pending")
    shipping_service = models.CharField(max_length=100, choices=SHIPPING_SERVICE, default="none", null=True, blank=True)
    tracking_id = models.CharField(max_length=100, default=None, null=True, blank=True)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)
    color = models.CharField(max_length=100, null=True, blank=True)
    size= models.CharField(max_length=100, null=True, blank=True)
    price= models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    initiate_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Total amount before discount")
    saved = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Amount saved")
    coupon = models.ManyToManyField(Coupon,blank=True)
    applied_coupon = models.BooleanField(default=False)
    item_id = ShortUUIDField(length=5, max_length= 25, alphabet="0123456789")
    vendor = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True, blank=True,related_name="vendor_order_items")
    date = models.DateTimeField(default=timezone.now)

    def order_id(self):
        return f"{self.order.order_id}"


    def __str__(self):
        return self.item_id
    
    class Meta:
        ordering = ["-date"]
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviews")
    user = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.IntegerField(choices=RATING, default=None)
    review = models.TextField()
    reply = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} review on {self.product.name}"
    
    class Meta:
        ordering = ["-date"]