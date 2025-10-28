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

import requests

# from plugin.tax_calculation import tax_calculation

# Create your views here.


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
def product_detail(request, slug):
    # Retrieve a single product based on the provided slug and its published status
    product = store_models.Product.objects.get(slug= slug, status="Published")
    related_products = store_models.Product.objects.filter(category=product.category, status="Published").exclude(id=product.id)#[:4]
    product_stock_range = range(1, product.stock + 1)

    # Putting average rating in views.py, this is extra from ChatGPT:
    avg = product.average_rating()

    if avg is None:
        avg_rating = 0.0
        avg_round = 0
    else:
        avg_rating = float(avg) 
        avg_round = int(round(avg_rating))



    context = {
        'product': product,
        'related_products': related_products,
        "product_stock_range" : product_stock_range,
        "avg_rating": avg_rating,
        "avg_round": avg_round,
    }
    # Render the 'product_detail.html' template with the product context
    return render (request, 'store/product_detail.html', context)


@require_POST
# making add to cart view: 
def add_to_cart(request, product_id): 
    
    id = product_id or request.POST.get("id") or request.GET.get("id")
    qty_raw = request.POST.get("qty") or request.GET.get("qty")
    color = request.POST.get("color") or request.GET.get("color")
    size = request.POST.get("size") or request.GET.get("size")
    cart_id = request.POST.get("cart_id") or request.GET.get("cart_id")

    if not id or not qty_raw or not cart_id:
        return JsonResponse({"error": "Missing id, qty or cart_id"}, status=400)

    try:
        qty = int(qty_raw)
        if qty <= 0:
            return JsonResponse({"error": "qty must be a positive integer"}, status=400)
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid qty"}, status=400)

    request.session['cart_id'] = cart_id

    try:
        product = store_models.Product.objects.get(status="Published", id=id)
    except store_models.Product.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=404)

    if qty > product.stock:
        return JsonResponse({"error": "Requested quantity exceeds available stock"}, status=400)

    existing_item = store_models.Cart.objects.filter(cart_id=cart_id, product=product).first()

    item_sub_total = Decimal(product.price) * Decimal(qty)
    item_shipping = Decimal(product.shipping) * Decimal(qty)
    item_total = item_sub_total + item_shipping

    if not existing_item:
        cart_item = store_models.Cart(
            product=product, qty=qty, price=product.price, color=color,
            size=size, sub_total=item_sub_total, shipping=item_shipping,
            total=item_total, user=(request.user if request.user.is_authenticated else None),
            cart_id=cart_id
        )
        cart_item.save()
        message = "Item added to cart"
    else:
        existing_item.qty = qty
        existing_item.price = product.price
        existing_item.color = color
        existing_item.size = size
        existing_item.sub_total = item_sub_total
        existing_item.shipping = item_shipping
        existing_item.total = item_total
        existing_item.user = (request.user if request.user.is_authenticated else None)
        existing_item.save()
        cart_item = existing_item
        message = "Cart updated"

    qs = store_models.Cart.objects.filter(cart_id=cart_id)
    total_cart_items = qs.count()
    agg = qs.aggregate(sub_total=Sum('sub_total'))
    cart_sub_total_val = agg.get('sub_total') or Decimal("0.00")

    cart_sub_total_str = "{:,.2f}".format(cart_sub_total_val)
    items_sub_total_str = "{:,.2f}".format(cart_item.sub_total)

    return JsonResponse({
        "message": message,
        "total_cart_items": total_cart_items,
        "cart_sub_total": cart_sub_total_str,
        "items_sub_total": items_sub_total_str,
    })




def clear_cart_items(request):
    try:
        cart_id = request.session['cart_id']
        store_models.Cart.objects.filter(cart_id= cart_id).delete()
    except:
        pass

    return

def checkout(request,order_id):
    order =store_models.Order.objects.get(order_id=order_id)

    context = {
        "order": order
    }
    return render (request, "store/checkout.html", context)


def coupon_apply(request, order_id):
    try:
        order = store_models.Order.objects.get(order_id=order_id)
        order_items = store_models.OrderItem.objects.filter(order=order)
    except store_models.Order.DoesNotExist:
        return redirect ("store:cart")
    

    if request.method == "POST":
        coupon_code = request. POST.het("coupon_code")

        if not coupon_code:
            messages.error(request,"No coupon entered")
            return redirect ("store:checkout", order.order_id)
        try:
            coupon = store_models.Coupon.objects.get(code=coupon_code)
        except store_models.Coupon.DoesNotExist:
            messages.error(request,"Coupon does not exist")
            return redirect("store:checkout",order,order_id)
        
        if coupon in order.coupon.all():
            messages.error(request, "Coupon already activated")
            return redirect("store:checkout", order.order_id)
        
        else:
            total_discount = 0
            for item in order_items:
                if coupon.vendor == item.product.vendor and coupon not in item.coupon.all():
                    item_discount = item.total * coupon.discount /100
                    total_discount = item_discount

                    item.coupon.add(coupon)
                    item.total -= item_discount
                    item.saved += item_discount
                    item.save()
            
            if total_discount > 0:
                order.coupons.add(coupon)
                order.total -= total_discount
                order.sub_total -= total_discount
                order.saved += total_discount
                order.save()

        messages.success(request,"Coupon activated")
        return redirect("store:checkout",order.order_id)
        
def clear_cart_items(request):
    try:
        cart_id = request.session['cart_id']
        store_models.Cart.objects.filter(cart_id=cart_id).delete()
    except:
        pass

    return


def get_paypal_access_token():
    token_url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"

    data = {'grant_type', 'client_credentials'}
    auth = (settings.PAYPAL_CLIENT_ID , settings.PAYPAL_SECRET_ID)
    response = requests.post (token_url, data=data, auth= auth)

    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception(f"failed to get access token from Paypal. Status code: {response.status_code}")
    

def paypal_payment_verify(request, order_id):
    order = store_models.Order.objects.get(order_id = order_id)

    transaction_id = request.GET.get("transaction_id")
    paypal_api_url = f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{transaction_id}"
    headers = {
        'Content-Type' : 'application/json',
        'Authorization': f"Bearer {get_paypal_access_token()}"
    }
    response = requests.get (paypal_api_url,headers=headers)

    if response.status_code == 200:
        paypal_order_data = response.json()
        paypal_payment_status = paypal_order_data['status']
        payment_method = "PayPal"

        if paypal_payment_status == "COMPLETED":
            if order.payment_status == "Processing":
                order.payment_status = "Paid"
                order.payment_method = payment_method
                order.save()
                clear_cart_items(request)

                return redirect(f"/payment_status/{order.order_id}/payment_status=paid")
   
    else:
        return redirect (f"/paymentstatus/{order.order_id}/payment_status=failed")

def payment_status(request,order_id):
    order =store_models.Order.objects.get(order_id=order_id)

    context = {
        "order": order
    }
    return render(request, "store/payment_status.html",context)
