# This line imports the models from your Django app called store, and gives them a nickname or alias: store_models.
# Importing Django’s built-in admin module and your app’s models (store.models) using an alias (store_models).
from django.contrib import admin
# Register your models here.
from store import models as store_models

class GalleryInline(admin.TabularInline):
    model = store_models.Gallery

class VariationInline(admin.TabularInline):
    model = store_models.Variation
    
class VariantItemInline(admin.TabularInline):
    model = store_models.VariantItem


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title','image']
    list_editable = ['image']
    prepopulated_fields = {'slug': ('title',)}


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name','category','price','regular_price','stock','status','featured','vendor','date']
    search_fields = ['name','category__name']
    list_filter = ['status','category','featured',]
    inlines = [GalleryInline, VariationInline]
    prepopulated_fields = {'slug': ('name',)}

class VariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'name']
    search_fields = ['product__name', 'name']
    inlines = [VariantItemInline]
    
class VariantItemAdmin(admin.ModelAdmin):
    list_display = ['variant', 'title', 'content']
    search_fields = ['variant__name', 'title']

class GalleryAdmin(admin.ModelAdmin):
    list_display = ['product', 'gallery_id']
    search_fields = ['product__name', 'gallery_id']

class CartAdmin(admin.ModelAdmin):
    list_display = ['cart_id','user', 'product', 'quantity', 'price','total','date']
    search_fields = ['cart_id','user__username', 'product__name']
    list_filter = ['date', 'product']   
    
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount', 'vendor']
    search_fields = ['code','vendor__username']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'customer', 'total','payment_status', 'order_status', 'payment_method', 'date']
    list_editable = ['payment_status','order_status','payment_method']
    search_fields = ['order_id','customer__username']
    list_filter = ['payment_status', 'order_status']

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['item_id','order', 'product', 'quantity', 'price', 'total']
    search_fields = ['item_id','order__order_id','product__name']
    list_filter = ['order__date']

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'active', 'date']
    search_fields = ['product__name', 'user__username']
    list_filter = ['active','rating']


admin.site.register(store_models.Category, CategoryAdmin)
admin.site.register(store_models.Product, ProductAdmin)
admin.site.register(store_models.Variant, VariantAdmin)
admin.site.register(store_models.VariantItem, VariantItemAdmin)
admin.site.register(store_models.Gallery, GalleryAdmin)
admin.site.register(store_models.Cart, CartAdmin)
admin.site.register(store_models.Coupon, CouponAdmin)
admin.site.register(store_models.Order, OrderAdmin)
admin.site.register(store_models.OrderItem, OrderItemAdmin)
admin.site.register(store_models.Review, ReviewAdmin)
