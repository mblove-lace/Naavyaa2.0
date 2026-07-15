# This page will:
# 1. get all Product objects from your database where status = "Published".
# 2. Passes them into a dictionary (context) under the key "products".
# 3. Renders the template store/index.html with this context.

from decimal import Decimal
from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.urls import reverse
from plugin.service_fee import calculate_service_fee
from store import models as store_models
from django.http import JsonResponse
from django.conf import settings
from decimal import Decimal,InvalidOperation
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Sum

from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from plugin.tax_calculation import tax_calculation
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.template.loader import render_to_string

import json
import razorpay

from customer import models as customer_models
from vendor import models as vendor_models

from plugin.tax_calculation import tax_calculation

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
# // -------------------------------------------- ---------------------------- -----------------------------------------//
# // -------------------------------------------- Understanding how DATA moves -----------------------------------------//



def index(request):
    # store_models.Product - References a Django model                     called Product from the store_models module
    # .objects - This is Django's default model manager that provides database query methods
    # .filter(status="Published") - Applies a WHERE clause to only return records where the status field matches "Published"
    # .get is used for single record retrieval, while .filter is used for multiple records
    products = store_models.Product.objects.filter(status="Published")
    context = {'products': products}
    # Render the 'index.html' template with the products context
    # {'products': products} → This is the context dictionary that will be passed to the HTML template
    # We are sayig that the template should have access to a variable named 'products' which contains the filtered product records
    return render (request, 'store/index.html', context) 


# This view function is responsible for displaying the product catalogue based on a specific category. It takes a category_slug as a parameter, retrieves the corresponding category and products, applies filters based on size, color, and price if provided in the request, and renders the 'catalogue.html' template with the filtered products and category information.
def catalogue(request, category_slug):
    # get_object_or_404 is a Django shortcut function that retrieves an object from the database based on the given parameters.
    # If the object does not exist, it raises a 404 error. In this case, it tries to fetch a Category object where the slug field matches the category_slug parameter passed to the view. 
    # If no such category exists, it will return a 404 error page.
    category = get_object_or_404(store_models.Category, slug=category_slug)
    # This line retrieves all Product objects from the database that belong to the specified category (using category__slug to filter by the related Category's slug) and have a status of "Published". The resulting queryset is stored in the variable products.
    products = store_models.Product.objects.filter(category__slug=category_slug, status="Published")

    print("\n" + "="*80)
    print(f"DEBUG CATALOGUE: Category = {category.title}")
    print("="*80)
    # The following lines retrieve filter parameters (size, color, price) from the GET request. 
    # These parameters are used to further filter the products queryset based on the user's selections in the catalogue page.
    size = request.GET.get('size')
    # color: This line retrieves the value of the 'color' parameter from the GET request.
    #  If the user has selected a color filter on the catalogue page, this variable will hold that value (e.g., "Red", "Blue"). If no color filter is applied, it will be None.
    color = request.GET.get('color')
    # price: This line retrieves the value of the 'price' parameter from the GET request. Similar to size and color, this variable will hold the selected price filter value (e.g., "under500", "500-1000") if the user has applied a price filter on the catalogue page. If no price filter is applied, it will be None.
    price = request.GET.get('price')
    # The following lines apply additional filters to the products queryset based on the retrieved size, color, and price parameters.
    if size:
        products = products.filter(variants__variant_items__content=size).distinct()
    # The color filter is applied to the products queryset by checking if the color parameter is present in the GET request. If it is, the queryset is filtered to include only products that have a variant with a variant item whose content matches the selected color. The distinct() method is used to ensure that duplicate products are not returned in case multiple variants match the color filter.
    if color:
        products = products.filter(variants__variant_items__content=color).distinct()
    # The price filter is applied by checking the value of the price parameter and filtering the products queryset accordingly. Depending on the selected price range (e.g., "under500", "500-1000"), the queryset is filtered to include products that fall within that price range using Django's field lookups (e.g., price__lt, price__gte, price__lte).
    if price:
        if price == "under500":
            products = products.filter(price__lt=500)
        elif price == "500-1000":
            products = products.filter(price__gte=500, price__lte=1000)
        elif price == "1000-2000":
            products = products.filter(price__gte=1000, price__lte=2000)
        elif price == "above2000":
            products = products.filter(price__gt=2000)
    #  Applying sorting based on the sort parameter from the GET request. The sort_map dictionary defines the mapping of sorting options to their corresponding field names in the Product model. If a valid sort option is provided in the GET request, the products queryset is ordered accordingly using the order_by() method.
    sort = request.GET.get('sort')
    # sort_map is a dictionary that maps sorting options (like 'price_asc', 'price_desc', 'date_asc', 'date_desc') to their corresponding field names in the Product model. This allows the view to dynamically apply sorting based on the user's selection in the catalogue page.
    sort_map = {
        'price_asc':  'price',
        'price_desc': '-price',
        'date_asc':   'date',       # oldest first
        'date_desc':  '-date',      # newest first
    }
    # This line checks if the sort parameter from the GET request matches any of the keys in the sort_map dictionary. If it does, it applies the corresponding sorting to the products queryset using the order_by() method. For example, if sort is 'price_asc', it will order the products by price in ascending order; if sort is 'price_desc', it will order by price in descending order, and so on.
    if sort in sort_map:
        products = products.order_by(sort_map[sort])
    
    products_with_stock = []
    for product in products:
        # Get all variants
        size_variant = product.variants.filter(name__iexact="Size").first()
        color_variant = product.variants.filter(name__iexact="Color").first()
        
        # Calculate total stock
        if size_variant:
            total_stock = sum(s.stock for s in size_variant.variant_items.all())
        else:
            total_stock = product.stock
        
        # Attach variant data to product object
        product.total_stock = total_stock
        product.size_options = size_variant.variant_items.all() if size_variant else []
        product.color_options = color_variant.variant_items.all() if color_variant else []
        
        products_with_stock.append(product)

    # The context dictionary is created to pass the filtered products, category information, and selected filter values (size, color, price) to the template. This allows the template to display the products based on the applied filters and also indicate which filters are currently active.
    context = {
        'products': products_with_stock,
        'category': category,
        'selected_size': size,
        'selected_color': color,
        'selected_price': price,
        'selected_sort': sort, # This line adds the selected sorting option to the context, allowing the template to indicate which sorting option is currently active (e.g., by highlighting it in the sorting dropdown).
    }
    # Finally, the view renders the 'catalogue.html' template with the context containing the filtered products and category information. The template can then use this context to display the products in the catalogue page according to the user's selected filters.
    return render(request, 'store/catalogue.html', context)




# slug- the part of URL that uniquely identifies a particular page on a website in a form that is easy to read for both users and search engines
# 
def product_detail(request, slug):
     # Debug statement to confirm the function is being called (useful for troubleshooting).
    print("DEBUG: entered product_detail method")

    # Retrieve a single product based on the provided slug and its published status
    product = store_models.Product.objects.get(slug= slug, status="Published")
    # Fetch related products from the same category, excluding the current product, and limit to 4 random products. This is done to provide recommendations for similar products to the user. which wont be the same as the product they are currently viewing. The order_by('?') is used to randomize the selection of related products each time the page is loaded.
    related_products = store_models.Product.objects.filter(category=product.category, status="Published").exclude(id=product.id).order_by('?')[:4]
    size_variant =product.variants.filter(name__iexact="Size").first()
    sizes = size_variant.variant_items.all() if size_variant else []

    if sizes:
        total_variant_stock = sum(s.stock for s in sizes)
    else:
        total_variant_stock = product.stock

    product_stock_range = range(1, total_variant_stock + 1)

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
    wishlisted = False
    if request.user.is_authenticated:
        wishlisted = customer_models.Wishlist.objects.filter(
            user=request.user, 
            product=product).exists()
        print(f"DEBUG: checked if product is wishlisted for user in product_detail method - wishlisted={wishlisted}")



    context = {
        'product': product,
        'sizes': sizes,
        'related_products': related_products,
        "product_stock_range" : product_stock_range,
        "total_variant_stock": total_variant_stock,
        "avg_rating": avg_rating,
        "avg_round": avg_round,
        "wishlisted": wishlisted,
    }
    # print("DEBUG: When every attribute is being run in product_detail method")
    # Render the 'product_detail.html' template with the product context
    return render (request, 'store/product_detail.html', context)
    






#>>>>>>>>>>>>>> Making add to cart view >>>>>>>>>>>>>>>>>>:


# How will it contact with front end?
# >>> User clicks "Add to Cart"
        # ↓
# JavaScript/AJAX sends/executes a POST request
# sending: id, qty, color, size, cart_id
#         ↓
# SessionMiddleware intercepts the request FIRST. Sessionmiddleware is a piece of code that runs before your view function (add_to_cart) is executed. It checks if the incoming request has a session cookie and loads the corresponding session data from the database into request.session. This allows your view to access and modify session data (like cart_id) seamlessly without having to worry about how sessions are managed behind the scenes.
# (before your view even runs)
# loads the session from django_session table
# into request.session
#         ↓
# NOW your view add_to_cart() runs
#         ↓
# reads the POST data:
# id = request.POST.get("id")
# qty = request.POST.get("qty")
# cart_id = request.POST.get("cart_id")  ← comes from POST
#         ↓
# THEN this line runs:
# request.session['cart_id'] = cart_id   ← saved into session
#         ↓
# rest of the view logic runs...
#         ↓
# SessionMiddleware saves the updated 
# session back to django_session table
 
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

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    id      = data.get("id")
    qty     = data.get("qty")
    color   = data.get("color", "")
    size    = data.get("size")
    cart_id = data.get("cart_id")
        # Debug statement to print received parameters (useful for troubleshooting)
        # This is an f-string — allows inserting variables inside { }.
    print(f"DEBUG: Received - id={id}, qty_raw={qty}, color={color}, size={size}, cart_id={cart_id}")
    # request.session - What is a session? >>>   When a user visits your website, Django creates a small private storage box on the server specifically for that user. This is called a session.
    # This accesses the session data associated with the current user's request
    # Django's session object → stores data temporarily for a user.
    # 'cart_id' - A unique identifier for the user's shopping cart.This is the key you are storing in the session.
    # If 'cart_id' is not already in the session, generate a new one using store_models.generate_cart_id() and store it in the session.
    # This ensures that each user has a unique cart identifier stored in their session.
    # If there is no cart_id in the session, generate one and store it.
    # cart_id : You store the value of your cart_id inside the session.
    # where does django stores the session data? >>> Django can store session data in various places depending on your configuration (database, cache, file system, etc.). By default, Django creates django_session table in the database to store session data. Each session is identified by a unique session key (like cart_id) that is stored in a cookie on the user's browser.
    # Where is the Code That Instructs This? >>> The code that generates a cart_id is likely in the store_models module, specifically in a function named generate_cart_id(). This function would create a unique identifier (like a random string) to be used as the cart_id for the user's session.
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
    if size:
        variant_item = store_models.VariantItem.objects.filter(
            variant__product=product,
            variant__name__iexact="Size",
            content=size
        ).first()
        available_stock = variant_item.stock if variant_item else product.stock
    else:
        available_stock = product.stock

    if int(qty) > available_stock:
        return JsonResponse({"error": "Requested quantity exceeds available stock"}, status=400)
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
            # Calculating and setting the subtotal for this cart item (price * quantity). Subtotal and total are different- subtotal is the cost of the items in the cart, while total includes additional costs like shipping and taxes.
        cart.sub_total= Decimal(product.price) * Decimal(qty)
            # Calculating and setting the shipping cost for this cart item (shipping * quantity).
        # cart.shipping = Decimal(product.shipping) * Decimal(qty)
        cart.shipping = Decimal('0') 
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
        existing_cart_items.qty = int(qty)
        # Updating the price of the existing cart item to the product's current price.
        existing_cart_items.price = product.price
        # Updating the color of the existing cart item.
        existing_cart_items.color = color    
        # Updating the size of the existing cart item.
        existing_cart_items.size = size
        # Recalculating and updating the subtotal for the existing cart item.
        existing_cart_items.sub_total = Decimal(product.price) * Decimal(qty)
        # Recalculating and updating the shipping cost for the existing cart items.
        existing_cart_items.shipping = Decimal(product.shipping) * Decimal(qty)
            # Recalculating and updating the total cost for the existing cart item.
        existing_cart_items.total = existing_cart_items.sub_total + existing_cart_items.shipping   
        # Updating the user associated with the cart item for the existing cart item.
        # If the user is logged in, associate the cart item with that user; otherwise, set it to None.
        existing_cart_items.user = request.user if request.user.is_authenticated else None
            # Updating the cart_id for the existing cart item.
        existing_cart_items.cart_id = cart_id
        # Saving the updated cart item to the database. This actually updates the record in the Cart table.
        existing_cart_items.save()

        print(f"DEBUG: Updated cart item - qty set to {existing_cart_items.qty}")
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
            "item_sub_total": "{:,.2f}".format(existing_cart_items.sub_total) if existing_cart_items else "{:,.2f}".format(cart.sub_total)
         }, status=200)

# >>>>>>>>>>>>>> Making cart view >>>>>>>>>>>>>>>>>>:
#Checks whether session already contains a cart created earlier.
#  WHY ? Guests don't have  a user account. 
# For guest users (not logged in), the cart is identified by session-based cart_id.

def cart(request): 
    # if 'cart_id' is in the session, retrieve it; otherwise, set cart_id to None.m 
    if 'cart_id' in request.session:
        cart_id = request.session['cart_id']
    else:
        cart_id = None  
    # Fetching all cart items - QUERYSET (collection : list-like model objects) that match either the cart_id from the session or the logged-in user (if authenticated). From the the table- Cart, and putting it through the filter to check if the user is authenticated . So we use an OR condition to fetch cart items that match either the cart_id (for guests) or the user (for logged-in users). If the user is not authenticated, it will only filter by cart_id.
    items = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user)if request.user.is_authenticated else Q(cart_id=cart_id))
    cart_sub_total = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user)if request.user.is_authenticated else Q(cart_id=cart_id)).aggregate(sub_total= Sum("sub_total"))['sub_total']
    addresses = customer_models.Address.objects.filter(user=request.user).first() if request.user.is_authenticated else None

    try:
        addresses = customer_models.Address.objects.filter(user=request.user)
    except:
        addresses = None
    if not items:
        messages.warning(request, "Your cart is empty")
        return redirect ("store:index")
    
    context = {
        "items": items,
        "cart_sub_total": cart_sub_total,
        "addresses": addresses,
    }
    return render (request, "store/cart.html", context)





# Making delete cart item view >>>>>>>>>>>>>>>>>>:

# This view function is supposed to handle the deletion of a cart item from the shopping cart. 
# It expects a POST request with the item's ID, the product ID, and the cart ID to identify which item to delete. 
# After deleting the item, it returns a JSON response with a success message, the updated total number of items in the cart, and the new cart subtotal.
# 1. user clicks delete button from cart.html -  "<button type="button" class="cart-remove delete_cart_item" data-item-id="{{item.id}}" data-product-id="{{item.product.id}}">".
# 2. JavaScript captures the click event and sends an AJAX POST request to the delete_cart_item view, including the item ID, product ID, and cart ID in the request data.


def delete_cart_item(request):
    id = request.POST.get("id")
    item_id = request.POST.get("item_id")
    cart_id = request.POST.get("cart_id")
    print(f"DEBUG: Received - id={id}, item_id={item_id}, cart_id={cart_id}")
# 3. If the request did NOT send id OR item_id OR cart_id  → then stop and return an error. Stops the function and sends something back as the response.
# That means if one of the 3 required parameters (id, item_id, cart_id) is missing from the POST request, the function will return a JSON response with an error message and a 400 Bad Request status code. 
# This prevents the function from trying to delete a cart item without having all the necessary information to identify which item to delete.
    if not id or not item_id or not cart_id:
        return JsonResponse({"error": "Missing id, item_id or cart_id"}, status=400)
    print("DEBUG: All required fields present for deletion")

# 4. In short, 'Tries' to fetch the product and cart item from the database using the provided IDs. 
# How? >> "product = Product.objects.get(status="Published", id=id)" "
# If the product does not exist, it returns a 404 error.

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
            })




# Making create order view >>>>>>>>>>>>>>>>>>:
# In the urls_store.py, we have defined a URL pattern that maps to this view function. 
# When a user clicks the "Checkout" button on the cart page, it sends a POST request to this URL, which triggers the create_order function to execute. This function will handle the process of creating an order based on the items in the user's cart and the selected address for shipping.

def create_order(request):
    # The function only runs when user submits a form (POST request).
    #  If it's a GET request (like when the user first visits the checkout page), it will skip the order creation logic and simply redirect to the checkout page.
    if request.method == "POST":
        # This gets the selected shipping address ID from the checkout form submitted by the user. 
        # The form should have a field named "address" that contains the ID of the address the user chose for shipping.
        address_id = request.POST.get("address")
# if the address_id is not provided in the POST data, it means the user did not select a shipping address. 
# In this case, the function will add an error message to be displayed to the user and then redirect them back to the cart page,
#  so they can select an address before proceeding with the order creation.
        if not address_id:
            messages.error(request, "Please select an address")
            return redirect("store:cart")
        
        # This line tries to fetch the Address object from the database that 
        # 1. matches the provided address_id and 
        # 2. belongs to a logged-in user.
        # Using .filter().first() means: it will return the first matching address if it exists, or None if no matching address is found.
        address = customer_models.Address.objects.filter(user=request.user, id=address_id).first()
# If the address variable is None, it means that either the address does not exist or it does not belong to the logged-in user.
# This supports: If no address is found, it means either the address ID is invalid or the address does not belong to the user. In this case, the function will add an error message and redirect back to the cart page, prompting the user to select a valid address before proceeding with the order creation.
        if 'cart_id' in request.session:
            cart_id = request.session['cart_id']

        else:
            cart_id = None

            # If the user if logged in then Q(cart_id=cart_id) | Q(user=request.user)- This means:
            # 1. fetch cart items that either match the cart_id (for guests) OR
            # 2. belong to the logged-in user. 
            # This allows both guest users (identified by cart_id) and logged-in users (identified by user) to have their cart items included in the order creation process. 
            # 
            # But, If the user is not authenticated, it will only filter by cart_id, ensuring that only the relevant cart items are processed for the order.
        items = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user)if request.user.is_authenticated else Q(cart_id=cart_id))

        # This line calculates the subtotal of all cart items that match either the cart_id or belong to the logged-in user. It uses Django's aggregate function to sum up the sub_total field of all matching cart items and retrieves the result as 'sub_total'.
        # Cart.object is your model manager that allows you to query the Cart table in the database.
        # filter(Q(cart_id=cart_id) | Q(user=request.user)if request.user.is_authenticated else Q(cart_id=cart_id)) - 
        # This filters the cart items to include those that 
        # either match the cart_id (for guests) OR 
        # belong to the logged-in user (if authenticated). If the user is not authenticated, it will only filter by cart_id.
        cart_sub_total = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user)if request.user.is_authenticated else Q(cart_id=cart_id)).aggregate(sub_total= Sum("sub_total"))['sub_total']
        # This line calculates the total shipping cost for all cart items that match either the cart_id or belong to the logged-in user. Similar to the previous line, it uses Django's aggregate function to sum up the shipping field of all matching cart items and retrieves the result as 'shipping_total'. 

        cart_shipping_total = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user)if request.user.is_authenticated else Q(cart_id=cart_id)).aggregate(shipping_total= Sum("shipping"))['shipping_total']



# This block of code creates a new Order object and populates its fields based on the cart items and the selected address. 
# It calculates the order totals, including shipping and tax, and saves the order to the database. Then, it iterates through each cart item and creates corresponding OrderItem records linked to the order. Finally, it redirects the user to the checkout page for the newly created order.
        order = store_models.Order()
        # sub_total → total of all cart item prices before adding shipping and tax.
        order.sub_total = cart_sub_total
        order.customer = request.user 
        order.address = address
        if cart_sub_total < 2000:
            order.shipping = Decimal('150')
        else:
            order.shipping = Decimal('0')
        # tax_calculation(address.country, cart_sub_total) → This function calculates the tax amount based on the country of the shipping address and the cart subtotal. The tax is likely calculated as a percentage of the subtotal, and the specific tax rate may vary depending on the country. The calculated tax amount is then assigned to the order's tax field.
        order.tax = tax_calculation(address.country, cart_sub_total)
        # As my Naavyaa is not under GST taxing system, so I am not calculating tax for each item, instead I am calculating tax for the whole order based on the country of the shipping address and the cart subtotal. This simplifies the tax calculation process while still ensuring that the appropriate tax amount is applied to the order based on the customer's location.
        # order.total = order.sub_total + order.shipping + Decimal(order.tax)
        order.total = order.sub_total + order.shipping
        order.service_fee = calculate_service_fee(order.total)
        order.total += order.service_fee
        order.initial_total = order.total
        order.save()
        
        for i in items:
            store_models.OrderItem.objects.create(
                order=order,
                product=i.product,
                qty = i.qty,
                color = i.color,
                size = i.size,
                price = i.price,
                sub_total = i.sub_total,
                shipping = i.shipping,
                tax= tax_calculation(address.country, i.sub_total),
                total = i.total,
                initial_total = i.total, 
                vendor = i.product.vendor
            )

            order.vendors.add(i.product.vendor)
    return redirect("store:checkout", order.order_id)
         



def checkout(request,order_id):
   
#    if 'cart_id' in request.session:
#     cart_id = request.session['cart_id']
#    else:
#     cart_id = None
    
#     items = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user)if request.user.is_authenticated else Q(cart_id=cart_id))

#     cart_sub_total = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user)if request.user.is_authenticated else Q(cart_id=cart_id)).aggregate(sub_total= Sum("sub_total"))['sub_total']

    order =store_models.Order.objects.get(order_id=order_id)
    amount = int(order.total * 100)  # Razorpay expects amount in paise (1 INR = 100 paise)

    try: 
        razorpay_order = razorpay_client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1,
            })
    except Exception as e:
        print(f"Error occurred while creating Razorpay order: {e}")
        razorpay_order = None

    context = {
        "items": order.order_items,
        "cart_sub_total": order.sub_total,
        
        "order": order,
        "paypal_client_id": settings.PAYPAL_CLIENT_ID,
        "razorpay_order_id": razorpay_order['id'] if razorpay_order else None,
        "amount": amount,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
    }
    return render (request, "store/checkout.html", context)


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
        
def clear_cart_items(request):
    try:
        cart_id = request.session['cart_id']
        store_models.Cart.objects.filter(cart_id=cart_id).delete()
    except:
        pass

    return








# ====================================
# PAYPAL ACCESS TOKEN FUNCTION
# ====================================
# This function retrieves an access token from PayPal's API
# The access token is required to make authenticated requests to PayPal's payment verification endpoints
# Think of it like getting a temporary password to talk to PayPal's servers
# The flow: 
# 1. The server requests an access token from PayPal 
#    with "POST https://api-m.sandbox.paypal.com/v1/oauth2/token". the server makes a POST request to PayPal's token endpoint,
# Method: POST
# URL: https://api-m.sandbox.paypal.com/v1/oauth2/token
# Headers: Authorization (Basic Auth)
# Body: grant_type=client_credentials
# PayPal verifies your credentials and returns a token → Your server uses that token to verify payments with PayPal's API

# def get_paypal_access_token():
#     # token_url: The PayPal API endpoint URL where we request the access token
#     # This is PayPal's sandbox (testing) environment - for production, you'd use "https://api-m.paypal.com"
#     token_url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
    
# # This tells PayPal: "hI pAYpAL, Iwant an access token to authenticate my API requests.
# #  I'm using the client credentials grant type, which means I'm proving my identity with my app's Client ID and Secret."
 
#     data = {'grant_type': 'client_credentials'}  

#     # auth: A tuple containing our PayPal app credentials (Client ID and Secret)
#     # settings.PAYPAL_CLIENT_ID: Your PayPal app's Client ID (stored in Django settings.py for security)
#     # settings.PAYPAL_SECRET_ID: Your PayPal app's Secret key (like a password, also in settings.py)
#     # These credentials prove to PayPal that our app is authorized to make API requests
#     auth = (settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET_ID)
    
#     # requests.post(): Makes an HTTP POST request to PayPal's server
#     # token_url: Where we're sending the request
#     # data=data: The information we're sending (grant_type)
#     # auth=auth: Our credentials for authentication (requests will automatically encode these as Basic Auth)
#     # response: The object that stores PayPal's reply to our request
#     response = requests.post(token_url, data=data, auth=auth)

#     # Checking if the request was successful
#     # response.status_code: HTTP status code returned by PayPal (200 means success)
#     # 200: "OK" - the request succeeded
#     if response.status_code == 200:
#         # response.json(): Converts PayPal's JSON response into a Python dictionary
#         # ['access_token']: Extracts just the access token string from the response
#         # This token is like a temporary key that lets us make authenticated requests to PayPal
#         # We return this token so other functions can use it
#         return response.json()['access_token']
#     else:
#         # If something went wrong (status code is not 200), we raise an error
        
#         # Exception: A Python error that stops the program and shows an error message
#         # The error message includes the status code to help with debugging
#         raise Exception(f"failed to get access token from Paypal. Status code: {response.status_code}")
       


# # ====================================
# # PAYPAL PAYMENT VERIFICATION FUNCTION
# # ====================================
# # This function verifies that a PayPal payment was actually completed successfully
# # It's called after the user completes payment and returns to our site
# # It checks with PayPal's servers to confirm the payment is legitimate

# def paypal_payment_verify(request, order_id):
#     # request: The Django HTTP request object containing information about the user's request
#     # order_id: The unique identifier for the order we're verifying payment for
    
#     # Fetching the order from our database using the order_id
#     # store_models.Order: Our Django model representing an order
#     # .objects.get(): Database query that retrieves ONE order matching the criteria
#     # order_id=order_id: Finds the order where the order_id field matches the provided order_id
#     # order: Variable storing the Order object we retrieved from the database
#     order = store_models.Order.objects.get(order_id=order_id)

#     # Getting the PayPal transaction ID from the URL parameters
#     # request.GET: A dictionary-like object containing URL query parameters (everything after ? in the URL)
#     # .get("transaction_id"): Safely retrieves the value of the "transaction_id" parameter
#     # Example URL: /verify-payment/123/?transaction_id=ABC123XYZ
#     # transaction_id: The unique ID PayPal assigned to this payment transaction
#     transaction_id = request.GET.get("transaction_id")
    
#     # Building the PayPal API URL to check this specific transaction
#     # f-string: Allows us to insert the transaction_id variable into the URL
#     # This endpoint lets us query PayPal for details about a specific order/transaction
#     # paypal_api_url: The complete URL we'll send our verification request to
#     paypal_api_url = f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{transaction_id}"
    
#     # Setting up HTTP headers for our request to PayPal
#     # headers: A dictionary containing metadata about our request
#     headers = {
#         # 'Content-Type': Tells PayPal we're sending/expecting JSON formatted data
#         'Content-Type': 'application/json',
#         # 'Authorization': Proves to PayPal that we're authorized to access this information
#         # f"Bearer {get_paypal_access_token()}": Calls our function to get the access token
#         # "Bearer" is the authentication type, followed by the actual token
#         # This is like showing your ID card to prove who you are
#         'Authorization': f"Bearer {get_paypal_access_token()}"
#     }
    
#     # Making a GET request to PayPal to fetch transaction details
#     # requests.get(): Makes an HTTP GET request (retrieving information)
#     # paypal_api_url: The URL we're requesting from
#     # headers=headers: Includes our authentication and content-type information
#     # response: Stores PayPal's response containing the transaction details
#     response = requests.get(paypal_api_url, headers=headers)

#     # Checking if PayPal successfully returned the transaction information
#     # response.status_code: The HTTP status code from PayPal's response
#     # 200: Means "OK" - PayPal found the transaction and sent us the details
#     if response.status_code == 200:
#         # Converting PayPal's JSON response into a Python dictionary
#         # response.json(): Parses the JSON data from PayPal
#         # paypal_order_data: Dictionary containing all the transaction details
#         # Example: {'id': 'ABC123', 'status': 'COMPLETED', 'amount': {...}, ...}
#         paypal_order_data = response.json()
        
#         # Extracting the payment status from PayPal's response
#         # ['status']: Gets the value of the 'status' field from the dictionary
#         # paypal_payment_status: String indicating if payment was completed, pending, failed, etc.
#         # Possible values: "COMPLETED", "PENDING", "CANCELLED", "FAILED"
#         paypal_payment_status = paypal_order_data['status']
        
#         # Setting the payment method name that we'll store in our database
#         # payment_method: A string we'll save to remember this order was paid via PayPal
#         payment_method = "PayPal"

#         # Checking if PayPal confirms the payment was completed
#         # "COMPLETED": PayPal's status indicating the payment went through successfully
#         if paypal_payment_status == "COMPLETED":
#             # Additional check: only update if our order status is still "Processing"
#             # This prevents accidentally changing an order that's already been marked as paid
#             # order.payment_status: The current payment status stored in our database
#             if order.payment_status == "Processing":
#                 # Updating the order's payment status in our database
#                 # "Paid": Marks the order as successfully paid
#                 order.payment_status = "Paid"
                
#                 # Recording which payment method was used
#                 # Saves "PayPal" to the order record
#                 order.payment_method = payment_method
                
#                 # Saving the changes to the database
#                 # .save(): Commits all the changes we made to the order object
#                 # This actually updates the database record
#                 order.save()
                
#                 # Clearing the user's shopping cart since payment is complete
#                 # clear_cart_items(): A function (defined elsewhere) that removes items from the cart
#                 # request: Passed so the function knows which user's cart to clear
#                 clear_cart_items(request)



#                 customer_merge_data = {
#                     'order' :order,
#                     'order_items': order.order_items,
#                 }

#                 subject = f"New Order Placed"
#                 text_body = render_to_string('emails/order/customer_new_order_email.txt', customer_merge_data)
#                 html_body = render_to_string('emails/order/customer_new_order_email.html', customer_merge_data)

#                 msg = EmailMultiAlternatives(
#                     subject=subject, from_email=settings.FROM_EMAIL, to=[order.address.email], body=text_body
#                     )
#                 msg.attach_alternative(html_body, "text/html")
#                 msg.send()
#                 customer_models.Notification.objects.create(type="New Order", user=request.user)
                




#                 # vendor notification

#                 for item in order.order_items():
                    
#                     vendor_merge_data ={
#                         'item': item,
#                     }
#                     subject = f"New Order for {item.product.name}"
#                     text_body = render_to_string('emails/order/vendor_new_order_vendor_email.txt', vendor_merge_data)
#                     html_body = render_to_string('emails/order/vendor_new_order_vendor_email.html', vendor_merge_data)

#                     msg = EmailMultiAlternatives(
#                         subject=subject, from_email=settings.FROM_EMAIL, 
#                         to=[item.vendor.user.email], body=text_body
#                         )
#                     msg.attach_alternative(html_body, "text/html")
#                     msg.send()
#                     vendor_models.Notification.objects.create(type="New Order", user=item.vendor, order=item)

                   
                                                                             

#                 # Redirecting the user to a success page
#                 # redirect(): Django function that sends the user to a different URL
#                 # f-string: Builds the URL with the order_id
#                 # payment_status=paid: URL parameter indicating successful payment
#                 # This shows the user a "Payment Successful" page
#                 return redirect(f"/payment_status/{order.order_id}/payment_status=paid")
                
   
#     # If we reach here, either:
#     # 1. PayPal returned an error (status code != 200)
#     # 2. Payment status was not "COMPLETED"
#     # In either case, redirect to the failure page
#     else:
#         # Redirecting to a payment failed page
#         # Shows the user that something went wrong with their payment
        
#         # This inconsistency might cause a 404 error if the URL pattern doesn't match
#         return redirect(f"/paymentstatus/{order.order_id}/payment_status=failed")
      

# ====================================
# PAYMENT STATUS PAGE FUNCTION
# ====================================
# This view function displays a page showing whether the payment succeeded or failed
# It's the page users see after attempting to pay

def payment_status(request, order_id):
    # request: Django's HTTP request object with information about the user's request
    # order_id: The unique identifier for the order we want to show status for
    
    # Retrieving the order from the database
    # store_models.Order: Our Order model/database table
    # .objects.get(): Fetches exactly one order
    # order_id=order_id: Finds the order with this specific order_id
    # order: Variable storing the Order object we retrieved
    order = store_models.Order.objects.get(order_id=order_id)

    # Creating a context dictionary to pass data to the template
    # context: A dictionary containing all data we want available in the HTML template
    # The template can access this data to display order information
    context = {
        # "order": The key name used in the template (e.g., {{ order.order_id }})
        # order: The Order object we fetched from the database
        "order": order
    }
    
    # Rendering an HTML template with the context data
    # render(): Django function that combines a template with data and returns an HTTP response
    # request: The original request object (required by Django)
    # "store/payment_status.html": Path to the HTML template file
    # context: The data dictionary we created above
    # This returns a complete HTML page to show the user
    return render(request, "store/payment_status.html", context)


# ==================================== RAZORPAY PAYMENT VERIFICATION FUNCTION  ====================================
# Django protects against Cross-Site Request Forgery (CSRF) attacks by default, which can interfere with payment gateway callbacks.
# @csrf_exempt: This decorator tells Django to skip CSRF protection for this view, allowing it to accept requests from Razorpay's servers without requiring a CSRF token. This is necessary because Razorpay will send a POST request to this endpoint to verify the payment, and it won't include a CSRF token in that request. 
# By using @csrf_exempt, we ensure that our payment verification endpoint can receive and process Razorpay's callback without being blocked by Django's security measures.
@csrf_exempt
# This function verifies the payment made through Razorpay by checking the payment signature sent by Razorpay against the expected signature generated using our Razorpay credentials.
# If the verification is successful, it updates the order status to "Paid" and sends notifications to the customer and vendors. If the verification fails, it returns an error response.

def razorpay_payment_verify(request, order_id):
    order = get_object_or_404(store_models.Order, order_id=order_id)

    razorpay_order_id = request.POST.get("razorpay_order_id") or request.GET.get("razorpay_order_id")
    razorpay_payment_id = request.POST.get("razorpay_payment_id") or request.GET.get("razorpay_payment_id")
    razorpay_signature = request.POST.get("razorpay_signature") or request.GET.get("razorpay_signature")

    if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
        return JsonResponse({"success": False, "error": "Missing params"}, status=400)

    params_dict = {
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_signature": razorpay_signature,
    }

    # 1. Verify signature — isolated try/except
    try:
        razorpay_client.utility.verify_payment_signature(params_dict)
    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({"success": False, "error": "Signature verification failed"}, status=400)

    # 2. Update order — only runs if signature passed
    if order.payment_status == "Processing":
        order.payment_status = "Paid"      
        order.payment_method = "Razorpay"
        order.payment_id = razorpay_payment_id
        order.save()
        clear_cart_items(request)

        # 3. Emails — isolated so failure doesn't block response
        try:
            customer_merge_data = {
                'order': order,
                'order_items': order.order_items(),
            }
            subject = "New Order Placed"
            text_body = render_to_string('email/order/customer/customer_new_order.txt', customer_merge_data)
            html_body = render_to_string('email/order/customer/customer_new_order.html', customer_merge_data)
            msg = EmailMultiAlternatives(
                subject=subject, from_email=settings.FROM_EMAIL,
                to=[order.address.email], body=text_body
            )
            msg.attach_alternative(html_body, "text/html")
            msg.send()

            customer_models.Notification.objects.create(type="New Order", user=request.user)

            for item in order.order_items():
                vendor_merge_data = {'item': item}
                subject = f"New Order for {item.product.name}"
                text_body = render_to_string('email/order/vendor/vendor_new_order.txt', vendor_merge_data)
                html_body = render_to_string('email/order/vendor/vendor_new_order.html', vendor_merge_data)
                msg = EmailMultiAlternatives(
                    subject=subject, from_email=settings.FROM_EMAIL,
                    # change 1 item.vendor.user.email to item.vendor.email
                    to=[item.vendor.email], body=text_body
                )
                msg.attach_alternative(html_body, "text/html")
                msg.send()
                vendor_models.Notification.objects.create(type="New Order", user=item.vendor, order=item)

        except Exception as e:
            print(f"EMAIL ERROR (non-blocking): {e}")

    # 4. Always return JSON — frontend fetch() needs this
    return JsonResponse({"success": True})
