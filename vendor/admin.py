from django.contrib import admin

# Register your models here.
from vendor import models as vendor_models

class VendorAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'user','country','vendor_id', 'date')
    search_fields = ('store_name', 'vendor_id', 'user__username')
    list_filter = ('country','date',)
    prepopulated_fields = {'slug': ('store_name',)}

class PayoutAdmin(admin.ModelAdmin):
    list_display = ('payout_id','vendor', 'item', 'amount',  'date')
    search_fields = ( 'payout_id','vendor__store_name', 'item__order__order_id')
    list_filter = ('date','vendor')

class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'account_number', 'bank_name')
    search_fields = ('vendor__store_name', 'account_number', 'ifsc_code')
    list_filter = ['account_type'] 

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'order', 'seen', 'date')
    list_editable = ['order']


admin.site.register(vendor_models.Vendor, VendorAdmin)
admin.site.register(vendor_models.Payout, PayoutAdmin)
admin.site.register(vendor_models.BankAccount, BankAccountAdmin)
admin.site.register(vendor_models.Notification, NotificationAdmin)