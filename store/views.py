# This page will:
# 1. get all Product objects from your database where status = "Published".
# 2. Passes them into a dictionary (context) under the key "products".
# 3.Renders the template store/index.html with this context.


from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from store import models as store_models
from django.http import JsonResponse
from django.conf import settings
from decimal import Decimal,InvalidOperation
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Sum
from customer import models as customer_models
from django.contrib import messages
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

import requests

# from plugin.tax_calculation import tax_calculation



# // -------------------------------------------- ---------------------------- -----------------------------------------//
# // -------------------------------------------- Understanding how DATA moves -----------------------------------------//



def index(request):
    # store_models.Product - References a Django model class called Product from the store_models module
    # .objects - This is Django's default model manager that provides database query methods
    # .filter(status="Published") - Applies a WHERE clause to only return records where the status field matches "Published"
    # .get is used for single record retrieval, while .filter is used for multiple records
    products = store_models.Product.objects.filter(status="Published")
    context = {'products': products}
    # Render the 'index.html' template with the products context
    # {'products': products} → This is the context dictionary that will be passed to the HTML template
    # We are sayig that the template should have access to a variable named 'products' which contains the filtered product records
    return render (request, 'store/index.html', context) 

# slug- the part of URL that uniquely identifies a particular page on a website in a form that is easy to read for both users and search engines
# 
def product_detail(request, slug):
     # Debug statement to confirm the function is being called (useful for troubleshooting).
    print("DEBUG: entered product_detail method")

    # Retrieve a single product based on the provided slug and its published status
    product = store_models.Product.objects.get(slug= slug, status="Published")
    related_products = store_models.Product.objects.filter(category=product.category, status="Published").exclude(id=product.id)#[:4]
    product_stock_range = range(1, product.stock +1)

    # print("DEBUG: entered attributes of product_detail method")

    # Putting average rating in views.py, this is extra from ChatGPT:
    avg = product.average_rating()
    # print("DEBUG: entered average rating of the product in product_detail method")

    if avg is None:
        avg_rating = 0.0
        avg_round = 0
        print("DEBUG: entered conditional when no rating is done yet in product_detail method")
    else:
        avg_rating = float(avg) 
        avg_round = int(round(avg_rating))
        print("DEBUG: entered conditional when rating is done in product_detail method")



    context = {
        'product': product,
        'related_products': related_products,
        "product_stock_range" : product_stock_range,
        "avg_rating": avg_rating,
        "avg_round": avg_round,
    }
    # print("DEBUG: When every attribute is being run in product_detail method")
    # Render the 'product_detail.html' template with the product context
    return render (request, 'store/product_detail.html', context)
    



#>>>>>>>>>>>>>> Making add to cart view >>>>>>>>>>>>>>>>>>:
 
# Defines a view function that handles adding products to a shopping cart. Takes an HTTP request object and a product_id parameter (likely from URL routing).
# Django automatically passes product_id from the URL to this view function when it is called.
# creates a view function named add_to_cart. Where django passes request - contains information sent by the client (browser) and product_id - likely extracted from the URL pattern.

def add_to_cart(request): 
     # Debug statement to confirm the function is being called (useful for troubleshooting).
    print("DEBUG: entered the add_to_cart method")

# Getting product ID from URL parameter, POST data, or GET parameters
# Tries to get the product ID from three sources in order: URL parameter, POST data, or GET parameters. Uses the first non-empty value found.
# id= A variable where you are storing the product's ID (like 12, or 58).
# The HTTP request object that Django receives when someone visits a URL.
# request.GET.get("id") - This part looks for a value named "id" in the URL's query parameters (the part after ? in a URL).
# GET= This means the code is reading data passed in the URL.
# request.GET.get("id") : Reads the value of the "id" parameter from the URL.
# If the URL is:id=10 → this returns "10".

    id = request.POST.get("id")
    #  qty: Variable storing quantity of the product (1, 2, 3...)
    qty = request.POST.get("qty") 
    # color: Variable storing selected color of the product (like "red" or "blue")
    color = request.POST.get("color") 
    # size: Variable storing selected size of the product (like "M" or "L")
    size = request.POST.get("size") 
        # cart_id: Variable storing unique identifier for the shopping cart.
    cart_id = request.POST.get("cart_id")
        # Debug statement to print received parameters (useful for troubleshooting)
        # This is an f-string — allows inserting variables inside { }.
    print(f"DEBUG: Received - id={id}, qty_raw={qty}, color={color}, size={size}, cart_id={cart_id}")
    # request.session - This accesses the session data associated with the current user's request
    # Django's session object → stores data temporarily for a user.
    # 'cart_id' - A unique identifier for the user's shopping cart.This is the key you are storing in the session.
    # If 'cart_id' is not already in the session, generate a new one using store_models.generate_cart_id() and store it in the session.
    # This ensures that each user has a unique cart identifier stored in their session.
    # If there is no cart_id in the session, generate one and store it.
    # cart_id : You store the value of cart_id inside the session.
    request.session['cart_id'] = cart_id
    print(f"DEBUG: Session cart_id={request.session['cart_id']}")
# If the request did NOT send id OR qty OR cart_id → then stop and return an error. Stops the function and sends something back as the response.

    if not id or not qty or not cart_id:
        return JsonResponse({"error": "Missing id, qty or cart_id"}, status=400)
    print("DEBUG: All required fields present")

    # If something inside try fails → it jumps to the except block.
    try:
        # product is a Variable to store the product fetched from the database. 
        # store_models.Product.objects.get(...) - This line queries the database for a Product object that matches the given criteria.  

        product = store_models.Product.objects.get(status="Published", id=id)
    except store_models.Product.DoesNotExist:
        print("DEBUG: Product does not exist")
        return JsonResponse({"error": "Product not found"}, status=404)
        


    # existing_cart_items : What it stores: The first cart item found in the Cart table 

    # store_models.Cart.objects.filter(): fetches all cart items from the database (because there is no filter condition).
    # >>> How ? It uses the filter() method to search for cart items that match both the cart_id and product.
    # Cart → your Django model (database table) representing shopping cart items.
    # .objects → the default manager for the Cart model, which provides database query methods.
    # .filter(cart_id=cart_id, product=product) → This filters the Cart items to only those that match the given cart_id and product.
    # .first(): gets the first item from that list (or None if the list is empty).

    existing_cart_items = store_models.Cart.objects.filter(cart_id=cart_id,product=product).first()
    # Comparing the existing cart items with the current product ID to find if the product is already in the cart.
    if int(qty) > product.stock:
        return JsonResponse({"error": "Requested quantity exceeds available stock"}, status=404)
    print("DEBUG: Checked product stock availability")
    
    if not existing_cart_items:
        # Making a new cart row/item in the Cart table.
        cart = store_models.Cart()
        #Attaching the selected product to this cart item. 
        cart.product = product
        # Converting qty from string to integer and assigning it to the cart item's quantity.
        cart.qty = int(qty)
        # Setting the price of the cart item to the product's price.
        cart.price = product.price
        # Storing the selected color for this cart item.
        cart.color = color
        # Storing the selected size for this cart item.
        cart.size = size
            # Calculating and setting the subtotal for this cart item (price * quantity).
        cart.sub_total= Decimal(product.price) * Decimal(qty)
            # Calculating and setting the shipping cost for this cart item (shipping * quantity).
        cart.shipping = Decimal(product.shipping) * Decimal(qty)
            # Calculating and setting the total cost for this cart item (subtotal + shipping).
        cart.total = cart.sub_total + cart.shipping 
            # Associating the cart item with the current user if they are logged in.
        cart.user = request.user if request.user.is_authenticated else None
            # Assigning the cart_id to this cart item.
        cart.cart_id = cart_id
        # Saving the new cart item to the database. This actually creates the record in the Cart table.
        cart.save()
        # Debug statement to confirm a new cart item was created.
        print("DEBUG: Created new cart item")
        message = "Item added to cart successfully"

# The following line of codes: If an existing cart item is found for the given cart_id and product, update that cart item.
    else:
# Updating the existing cart item with new values.
        existing_cart_items.product = product
        # Increasing the quantity of the existing cart item by the new quantity.
        existing_cart_items.qty += int(qty)
        # Updating the price of the existing cart item to the product's current price.
        existing_cart_items.price = product.price
        # Updating the color of the existing cart item.
        existing_cart_items.color = color    
        # Updating the size of the existing cart item.
        existing_cart_items.size = size
        # Recalculating and updating the subtotal for the existing cart item.
        existing_cart_items.sub_total += Decimal(product.price) * Decimal(qty)
        # Recalculating and updating the shipping cost for the existing cart items.
        existing_cart_items.shipping += Decimal(product.shipping) * Decimal(qty)
            # Recalculating and updating the total cost for the existing cart item.
        existing_cart_items.total = existing_cart_items.sub_total + existing_cart_items.shipping   
        # Updating the user associated with the cart item for the existing cart item.
        # If the user is logged in, associate the cart item with that user; otherwise, set it to None.
        existing_cart_items.user = request.user if request.user.is_authenticated else None
            # Updating the cart_id for the existing cart item.
        existing_cart_items.cart_id = cart_id
        # Saving the updated cart item to the database. This actually updates the record in the Cart table.
        existing_cart_items.save()

        print("DEBUG: Updated existing cart item")
        # Message indicating the cart was updated successfully.
        message = "Cart updated in cart successfully"

# Calculating total items and subtotal in the cart after adding/updating the item. By getting all cart items matching the cart_id to calculate totals.
# Q - Used here to  combine multiple conditions using logical operators (AND, OR).

    total_cart_items = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(cart_id=cart_id))
    # calculating the subtotal of all items in the cart by summing up the sub_total field of each cart item that matches the cart_id.
    cart_sub_total = store_models.Cart.objects.filter(cart_id=cart_id).aggregate(sub_total= Sum("sub_total"))['sub_total']
# Now sending the updated cart info back to the client as a JSON response.
# JsonResponse - A Django class that helps create HTTP responses with JSON content. So, sending the request back to the front end in JSON format.
    return JsonResponse(
        {
            "message": message,
            "total_cart_items": total_cart_items.count(),
            # Formatting the cart subtotal to 2 decimal places before sending it in the response.
            "cart_sub_total": "{:,.2f}".format(cart_sub_total),
            # Formatting the existing cart item's subtotal to 2 decimal places if it exists; otherwise, formatting the cart's subtotal.
            "items_sub_total": "{:,.2f}".format(existing_cart_items.sub_total) if existing_cart_items else "{:,.2f}".format(cart.sub_total)
         }, status=200)

# >>>>>>>>>>>>>> Making cart view >>>>>>>>>>>>>>>>>>:
#Checks whether session already contains a cart created earlier.
#  WHY ? Guests don't have  a user account. 

def cart(request):
    if 'cart_id' in request.session:
        cart_id = request.session['cart_id']
    else:
        cart_id = None  
    items = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user)if request.user.is_authenticated else Q(cart_id=cart_id))
    cart_sub_total = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user)if request.user.is_authenticated else Q(cart_id=cart_id)).aggregate(sub_total= Sum("sub_total"))['sub_total']

    try:
        addresses = customer_models.Address.objects.filter(user=request.user)
    except:
        addresses = None
    if not items:
        messages.info(request, "Your cart is empty")
        return redirect ("store:index")
    
    context = {
        "items": items,
        "cart_sub_total": cart_sub_total,
        "addresses": addresses,
    }
    return render (request, "store/cart.html", context)

def delete_cart_item(request):
    id = request.POST.get("id")
    item_id = request.POST.get("item_id")
    cart_id = request.POST.get("cart_id")
    print(f"DEBUG: Received - id={id}, item_id={item_id}, cart_id={cart_id}")

    if not id and not item_id or not cart_id:
        return JsonResponse({"error": "Missing id, item_id or cart_id"}, status=400)
    print("DEBUG: All required fields present for deletion")

    try:
        product = store_models.Product.objects.get(status="Published", id=id)
    except store_models.Product.DoesNotExist:
        print("DEBUG: Product does not exist for deletion")
        return JsonResponse({"error": "Product not found"}, status=404)
    item = store_models.Cart.objects.get(product=product,id=item_id)
    item.delete()
    print("DEBUG: Cart item deleted successfully")
    total_cart_items = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user))
    cart_sub_total = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user)).aggregate(sub_total= Sum("sub_total"))['sub_total']
    return JsonResponse(
        {
            "message": "Item deleted successfully", 
            "total_cart_items": total_cart_items.count(),
            "cart_sub_total": "{:,.2f}".format(cart_sub_total) if cart_sub_total else "0.00",
            }, status=200)



# def clear_cart_items(request):
#     try:
#         cart_id = request.session['cart_id']
#         store_models.Cart.objects.filter(cart_id= cart_id).delete()
#     except:
#         pass

#     return

# def checkout(request,order_id):
#     order =store_models.Order.objects.get(order_id=order_id)

#     context = {
#         "order": order
#     }
#     return render (request, "store/checkout.html", context)


# def coupon_apply(request, order_id):
#     try:
#         order = store_models.Order.objects.get(order_id=order_id)
#         order_items = store_models.OrderItem.objects.filter(order=order)
#     except store_models.Order.DoesNotExist:
#         return redirect ("store:cart")
    

#     if request.method == "POST":
#         coupon_code = request. POST.het("coupon_code")

#         if not coupon_code:
#             messages.error(request,"No coupon entered")
#             return redirect ("store:checkout", order.order_id)
#         try:
#             coupon = store_models.Coupon.objects.get(code=coupon_code)
#         except store_models.Coupon.DoesNotExist:
#             messages.error(request,"Coupon does not exist")
#             return redirect("store:checkout",order,order_id)
        
#         if coupon in order.coupon.all():
#             messages.error(request, "Coupon already activated")
#             return redirect("store:checkout", order.order_id)
        
#         else:
#             total_discount = 0
#             for item in order_items:
#                 if coupon.vendor == item.product.vendor and coupon not in item.coupon.all():
#                     item_discount = item.total * coupon.discount /100
#                     total_discount = item_discount

#                     item.coupon.add(coupon)
#                     item.total -= item_discount
#                     item.saved += item_discount
#                     item.save()
            
#             if total_discount > 0:
#                 order.coupons.add(coupon)
#                 order.total -= total_discount
#                 order.sub_total -= total_discount
#                 order.saved += total_discount
#                 order.save()

#         messages.success(request,"Coupon activated")
#         return redirect("store:checkout",order.order_id)
        
# def clear_cart_items(request):
#     try:
#         cart_id = request.session['cart_id']
#         store_models.Cart.objects.filter(cart_id=cart_id).delete()
#     except:
#         pass

#     return


# def get_paypal_access_token():
#     token_url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"

#     data = {'grant_type', 'client_credentials'}
#     auth = (settings.PAYPAL_CLIENT_ID , settings.PAYPAL_SECRET_ID)
#     response = requests.post (token_url, data=data, auth= auth)

#     if response.status_code == 200:
#         return response.json()['access_token']
#     else:
#         raise Exception(f"failed to get access token from Paypal. Status code: {response.status_code}")
    

# def paypal_payment_verify(request, order_id):
#     order = store_models.Order.objects.get(order_id = order_id)

#     transaction_id = request.GET.get("transaction_id")
#     paypal_api_url = f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{transaction_id}"
#     headers = {
#         'Content-Type' : 'application/json',
#         'Authorization': f"Bearer {get_paypal_access_token()}"
#     }
#     response = requests.get (paypal_api_url,headers=headers)

#     if response.status_code == 200:
#         paypal_order_data = response.json()
#         paypal_payment_status = paypal_order_data['status']
#         payment_method = "PayPal"

#         if paypal_payment_status == "COMPLETED":
#             if order.payment_status == "Processing":
#                 order.payment_status = "Paid"
#                 order.payment_method = payment_method
#                 order.save()
#                 clear_cart_items(request)

#                 return redirect(f"/payment_status/{order.order_id}/payment_status=paid")
   
#     else:
#         return redirect (f"/paymentstatus/{order.order_id}/payment_status=failed")

# def payment_status(request,order_id):
#     order =store_models.Order.objects.get(order_id=order_id)

#     context = {
#         "order": order
#     }
#     return render(request, "store/payment_status.html",context)
