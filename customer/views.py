# What does this view do?
# This view displays the customer's dashboard with their orders, total spending, and unread notifications.
# When a user is logged-in and accesses the dashboard URL, this view retrieves the relevant data from the database and renders it in the "customer/dashboard.html" template.
# The @login_required decorator ensures that only authenticated users can access this view. If a user is not logged in, they will be redirected to the login page.
# Fetch the customer's orders, total spending, and unread notifications.




# render the dashboard template with the retrieved data in the context dictionary. And Redict - Sends the user to another URL (after login, form submit, etc.).
from django.shortcuts import render, redirect
# JsonResponse - This class allows you to return JSON-encoded responses from your views, which is useful for AJAX requests or APIs.
from django.http import JsonResponse
# messages - This module provides a way to store messages in one request and retrieve them for display in a subsequent request (e.g., after a form submission).
from django.contrib import messages
# models - This module provides the base class for defining database models in Django, allowing you to create and manage your application's data structure.
from django.db import models
# login_required - This decorator is used to restrict access to a view to only authenticated users. If a user is not logged in, they will be redirected to the login page.
from django.contrib.auth.decorators import login_required
# check_password - This function is used to verify a plain-text password against a hashed password stored in the database. It returns True if the passwords match, and False otherwise.
from django.contrib.auth.hashers import check_password

# Importing models from the store and customer apps to access the Order and Notification models, respectively.
from store import models as store_models
# Importing models from the customer app to access the Notification model, which is used to fetch unread notifications for the user.
from customer import models as customer_models

# Create your views here.
# Django checks if the user is authenticated before allowing access to the dashboard view. 
# If the user is not authenticated, they will be redirected to the login page.
# This is powered by Django's built-in authentication system, which manages user sessions and authentication status.
@login_required
def dashboard(request):
    # store_models.Order → My database table (model), objects → The manager that allows you to query the database for instances of the Order model, filter() → A method that filters the queryset based on the given criteria (in this case, orders belonging to the logged-in user).
    # What SQL this roughly becomes: SELECT * FROM store_order WHERE customer_id = request.user.id;
    # Output comes: A queryset of Order objects that belong to the currently logged-in user (request.user).
    orders = store_models.Order.objects.filter(customer=request.user)
# aggregate() is a method that performs an aggregation operation on the queryset. 
# In this case, it calculates the total spending by summing the "total" field of all orders for the logged-in user.
# The result of the aggregation is a dictionary with the key "total" containing the sum of the "total" field for all matching orders.
# Equivalent SQL: SELECT SUM(total) AS total FROM store_order WHERE customer_id = request.user.id;
# What Django does: It executes the SQL query and returns a dictionary with the key "total" containing the sum of the "total" field for all orders that match the filter criteria (customer=request.user).
    total_spent =store_models.Order.objects.filter(
        customer=request.user).aggregate(total = models.Sum("total"))["total"]
    # Fetch unread notifications for the logged-in user.
    # user = current logged-in user (request.user), seen=False → Filter notifications that have not been marked as seen.
    # SQL equivalent: SELECT * FROM customer_notification WHERE user_id = request.user.id AND seen = False;
    # output: A queryset of Notification objects that belong to the currently logged-in user and have not been marked as seen.
    notis = customer_models.Notification.objects.filter(user=request.user,seen=False)

    # Fetch all wishlist items for this user
    # Each Wishlist object has a .product ForeignKey to the Product model
    wishlist = customer_models.Wishlist.objects.filter(user=request.user)

    # Fetch all saved delivery addresses for this user
    addresses = customer_models.Address.objects.filter(user=request.user)

    # Fetch all product reviews written by this user
    reviews = store_models.Review.objects.filter(user=request.user)
# Creating a context dictionary to pass the retrieved data (orders, total spending, and unread notifications) to the template for rendering.
    context = {
        # In my template, I can access the orders using {{ orders }}, total spending using {{ total_spent }}, and unread notifications using {{ notis }}.
        "orders": orders,
        "total_spent": total_spent,
        "notis": notis,
        "addresses": addresses,
        "reviews": reviews,
        "wishlist": wishlist if hasattr(customer_models, 'Wishlist') else [],
    }
# Returning the rendered template with the context data.
    return render(request, "customer/dashboard.html", context)

# @login_required
# def orders(request):
#     # Fetch all orders for the logged-in user
#     orders = store_models.Order.objects.filter(customer=request.user)
#     context = {
#         "orders": orders,
#     }
#     return render(request, "customer/orders.html", context)
#

# This view displays the details of a specific order for the logged-in user. 
# It retrieves the order based on the provided order_id and ensures that the order belongs to the current user. The order details are then passed to the "customer/order_detail.html" template for rendering.
# @login_required ensures that only authenticated users can access this view, and if a user is not logged in, they will be redirected to the login page.
@login_required
# order_id is a parameter that is passed to the view, typically from the URL. It represents the unique identifier of the order that the user wants to view.
def order_detail(request, order_id):
    # Fetch the specific order for the logged-in user.
    # Here, we are using the get() method to retrieve a single Order object that matches the given order_id and belongs to the current user (request.user). If no such order exists, it will raise a DoesNotExist exception.
    order = store_models.Order.objects.get(order_id=order_id, customer=request.user)

    order_items = order.order_items()
    # context dictionary to pass the retrieved order to the template for rendering. In the template, you can access the order details using {{ order }}.

    context = {
        "order": order,
        "order_items": order_items,
    }
    return render(request, "customer/order_detail.html", context)
# This view displays the details of a specific order item for the logged-in user. 
# Fetches the whole order reciept ...one order can have multiple order items. Example: Order O-69739 contains both a "Mull Cotton Saree" and a "Hand Print Kurti".  
# Order_detail shows you the full O-69739 page — both items, the total (₹2520), payment status, shipping address, everything about that order as a whole.
# It retrieves the order item based on the provided order_item_id and ensures that the order item belongs to an order that belongs to the current user. 
# The order item details are then passed to the "customer/order_item_detail.html" template for rendering.
# Why am I commenting out this def order_item_detail?
# Order_item_detail entails pecific item within that order. In th eprevious example of O-69739,if I click on Order_item_detail for the O-69739, order_item_detail shows you just the Saree row — its specific size, color, vendor (which weaver made it), and that item's individual shipping tracking number if it ships separately.
# @login_required
# def order_item_detail(request, order_item_id):
#     # Fetch the specific order item for the logged-in user
#     order_item = store_models.OrderItem.objects.get(id=order_item_id, order__customer=request.user)
#     context = {
#         "order_item": order_item,
#     }
#     return render(request, "customer/order_item_detail.html", context)