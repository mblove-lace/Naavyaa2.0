# Import the path function from Django's URL routing system
# This is used to define URL patterns
from django.urls import path

# Import the views module from your 'store' app
# This gives access to all view functions defined in store/views.py
from store import views

# Set the application namespace to 'store'
# This allows you to reference URLs as 'store:index' or 'store:product_detail'
# when using reverse() or {% url %} template tags
app_name = 'store'


# Define the list of URL patterns for this app
urlpatterns = [
      # Route: "" (empty string = root URL or base /starting point of a URL path of this app)
      
    # View: calls views.index function when this URL is accessed
    # Name: 'index' - used for reverse URL lookups
    # Full URL reference: 'store:index'
    path("", views.index, name='index'),
    # Route: "detail/<slug>/" - captures a slug parameter from the URL
    # View: calls views.product_detail function, passing the captured slug
    # Name: 'product_detail' - used for reverse URL lookups
    # Full URL reference: 'store:product_detail'
    # Example URL: "detail/my-product-name/" would call views.product_detail(request, slug="my-product-name")
    path("detail/<slug>/", views.product_detail, name='product_detail'),
    
    path ("add_to_cart/",views.add_to_cart,name= "add_to_cart"),
    path ("cart/",views.cart,name= "cart"),
    path ("delete_cart_item/",views.delete_cart_item,name= "delete_cart_item"),
    # path ("create_order/",views.create_order,name= "create_order"),
    # path ("checkout/<order_id>/",views.checkout,name= "checkout"),
    # path ("coupon_apply/<order_id>/",views.coupon_apply,name= "coupon_apply"),
    # path ("paypal_payment_verify/<order_id>/",views.paypal_payment_verify,name= "paypal_payment_verify"),
    path ("razorpay_payment_verify/<order_id>/",views.razorpay_payment_verify,name= "razorpay_payment_verify"),
]
