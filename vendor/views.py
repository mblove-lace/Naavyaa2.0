from django.shortcuts import render

# importing from .views import 
# this import is used to import the views from the current directory's views.py file. What is current directory? The current directory is the directory where this file (vendor/views.py) is located.
# It allows us to use the functions defined in views.py within this file.
        # from django.contrib.auth.decorators import login_required
        # from store import models as store_models
        # from vendor import models as vendor_models
        # from django.db import models

        # @login_required
        # def dashboard(request):
        #     product = store_models.Product.objects.filter(vendor=request.user)
        #     orders = store_models.OrderItem.objects.filter(vendors=request.user)
        #     revenue = store_models.OrderItem.objects.filter(vendors=request.user).aggregate(total = models.Sum('total'))['total']
        #     notis = vendor_models.Notification.objects.filter(vendor=request.user, seen=False)
        #     reviews = store_models.Review.objects.filter(product__vendor=request.user)


