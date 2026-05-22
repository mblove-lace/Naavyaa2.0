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

from django.views.decorators.http import require_POST

# Importing models from the store and customer apps to access the Order and Notification models, respectively.
from store import models as store_models
# Importing models from the customer app to access the Notification model, which is used to fetch unread notifications for the user.
from customer import models as customer_models

from userauths.models import Profile

from django.contrib.auth import update_session_auth_hash

# Create your views here.
# Django checks if the user is authenticated before allowing access to the dashboard view. 
# If the user is not authenticated, they will be redirected to the login page.
# This is powered by Django's built-in authentication system, which manages user sessions and authentication status.
@login_required
def dashboard(request):
    # putting profile in dashboard view because I want the profile edit form to be on the dashboard page itself. 
    # So when user clicks on "Edit Profile" in the sidebar, they are taken to the dashboard page where they can edit their profile details. This way, I can reuse the same dashboard template for both displaying the dashboard and editing the profile, instead of creating a separate profile.html template.
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST" and "full_name" in request.POST:
        profile.full_name = request.POST.get("full_name")
        profile.mobile = request.POST.get("mobile")
        profile.save()

        old_password = request.POST.get("old_password")
        new_password1 = request.POST.get("new_password1")
        new_password2 = request.POST.get("new_password2")

        if old_password:
            if not check_password(old_password, request.user.password):
                messages.error(request, "Current password is incorrect.")
                return redirect("customer:dashboard")

            if new_password1 != new_password2:
                messages.error(request, "New passwords do not match.")
                return redirect("customer:dashboard")

            if len(new_password1) < 6:
                messages.error(request, "Password must be at least 6 characters.")
                return redirect("customer:dashboard")

            request.user.set_password(new_password1)
            request.user.save()
            update_session_auth_hash(request, request.user)  # keeps user logged in
            messages.success(request, "Password changed successfully.")
            return redirect("customer:dashboard")


        messages.success(request, "Profile updated successfully.")
        return redirect("customer:dashboard")

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
    notis = customer_models.Notification.objects.filter(user=request.user).order_by("-date")
    unread_count = notis.filter(seen=False).count()

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
        "profile": profile,
        "orders": orders,
        "total_spent": total_spent,
        "notis": notis,
        "unread_count": unread_count,
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
        "active_nav": "orders",
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


# ------------ Wishlist Views ------------
@login_required
def wishlist_list(request):
    wishlist_list = customer_models.Wishlist.objects.filter(user=request.user)
    context = {
        "wishlist_list": wishlist_list,
    }
    return render(request, "customer/wishlist_list.html", context)

@login_required
def remove_from_wishlist(request, product_id):
    wishlist = customer_models.Wishlist.objects.filter(user=request.user, product_id=product_id).first()
    wishlist.delete()
    messages.success(request, "Item removed from wishlist.")
   
    return redirect('customer:wishlist_list')

@login_required
@require_POST
def toggle_wishlist(request, product_id):
    item = customer_models.Wishlist.objects.filter(
        user=request.user, product_id=product_id
    ).first()

    if item:
        item.delete()
        return JsonResponse({'status': 'removed'})
    else:
        customer_models.Wishlist.objects.create(
            user=request.user, product_id=product_id
        )
        return JsonResponse({'status': 'added'})

def add_to_wishlist(request, product_id):
    if request.user.is_authenticated:
        product = store_models.Product.objects.get(id=product_id)

        wishlist_item, created = customer_models.Wishlist.objects.get_or_create(
            user=request.user, product=product
        )
        
        if created:
            message = "Item added to wishlist."
        else:
            message = "Already in your wishlist."
            
        wishlist = customer_models.Wishlist.objects.filter(user=request.user)
        return JsonResponse({"message": message, "wishlist_count": wishlist.count()})
    else:
        return JsonResponse({"message": "Please log in to add to wishlist.", "wishlist_count": 0})
    




# notification views
# login is required to view notifications, as they are specific to each user. If a user is not logged in, they will be redirected to the login page.
@login_required

def notis(request):
    # Fetch unread notifications for the logged-in user. 
    # The filter() method is used to retrieve notifications that belong to the current user (request.user) and have not been marked as seen (seen=False). This allows the user to view only their unread notifications.
    notis = customer_models.Notification.objects.filter(user=request.user).order_by("-date")
    # Calculate the count of unread notifications by filtering the notifications queryset to include only those that have not been marked as seen (seen=False) and then counting the resulting queryset using the count() method. This gives the user an indication of how many unread notifications they have.
    unread_count = notis.filter(seen=False).count()
    # Creating a context dictionary to pass the retrieved notifications and the count of unread notifications to the template for rendering. In the template, you can access the notifications using {{ notis }} and the unread count using {{ unread_count }}.
    context = {
        "notis": notis,
        "unread_count": unread_count,
    }
    # Returning the rendered template with the context data. The "customer/notis.html" template will display the user's notifications and the count of unread notifications.
    return render(request, "customer/notis.html", context)



# This view allows the user to mark a specific notification as seen. It retrieves the notification based on the provided noti_id and ensures that the notification belongs to the current user. Once the notification is marked as seen, a success message is displayed, and the user is redirected back to the notifications page.
@login_required
# noti_id is a parameter that is passed to the view, typically from the URL. It represents the unique identifier of the notification that the user wants to mark as seen.
def mark_notis_seen(request, noti_id):
    # Fetch the specific notification for the logged-in user. Here, we are using the get() method to retrieve a single Notification object that matches the given noti_id and belongs to the current user (request.user). If no such notification exists, it will raise a DoesNotExist exception.
    noti = customer_models.Notification.objects.get(user=request.user, id=noti_id)
    # Mark the notification as seen by setting the seen attribute to True and saving the changes to the database. This allows the user to keep track of which notifications they have already viewed.
    noti.seen = True
    # save() method is called to persist the changes to the database. This updates the notification record to reflect that it has been marked as seen.
    noti.save()
# A success message is added to the messages framework using messages.success(). This message will be displayed to the user on the next page they visit, indicating that the notification has been marked as seen.
    messages.success(request, "Notification marked as seen.")
    # Redirect the user back to the notifications page.
    return redirect('customer:notis')



# Making CRUD views for the Address model. This allows users to manage their delivery addresses, including adding new addresses, editing existing ones, and deleting addresses they no longer need. Each view will ensure that only authenticated users can access these functionalities, and that users can only modify their own addresses.

@login_required
def addresses(request):
    addresses = customer_models.Address.objects.filter(user=request.user)
    context = {
        "addresses": addresses,
    }

    return render(request, "customer/addresses.html", context)


@login_required

def address_detail(request, address_id):
    address = customer_models.Address.objects.get(id=address_id, user=request.user)
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        mobile = request.POST.get("mobile")
        email = request.POST.get("email")
        country = request.POST.get("country")
        state = request.POST.get("state")
        city = request.POST.get("city")
        address_location = request.POST.get("address_location")
        zip_code = request.POST.get("zip_code")


        address.full_name = full_name
        address.mobile = mobile
        address.email = email   
        address.country = country
        address.state = state
        address.city = city
        address.address = address_location
        address.zip_code = zip_code
        address.save()
        messages.success(request, "Address updated successfully.")
    context = {
        "address": address,
    }
    return render(request, "customer/address_detail.html", context)


@login_required
def address_create(request): 
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        mobile = request.POST.get("mobile")
        email = request.POST.get("email")
        country = request.POST.get("country")
        state = request.POST.get("state")
        city = request.POST.get("city")
        address_location = request.POST.get("address_location")
        zip_code = request.POST.get("zip_code")

        customer_models.Address.objects.create(
            user=request.user,
            full_name=full_name,
            mobile=mobile,
            email=email,
            country=country,
            state=state,
            city=city,
            address=address_location,
            zip_code=zip_code
        )
        messages.success(request, "Address created successfully.")
        return redirect("customer:addresses")
    return render(request, "customer/address_create.html")

@login_required
def delete_address(request, address_id):
    address = customer_models.Address.objects.get(id=address_id, user=request.user)
    address.delete()
    messages.success(request, "Address deleted successfully.")
    return redirect("customer:addresses")









