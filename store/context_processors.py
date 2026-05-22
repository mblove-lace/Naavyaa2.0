# store/context_processors.py
from django.db.models import Q, Sum
from store import models as store_models
from customer.models import Wishlist

def cart_context(request):
    cart_id = request.session.get('cart_id', None)
    
    if request.user.is_authenticated:
        items = store_models.Cart.objects.filter(
            Q(cart_id=cart_id) | Q(user=request.user)
        )
    else:
        items = store_models.Cart.objects.filter(cart_id=cart_id) if cart_id else []

    order_total = sum(i.sub_total for i in items) if items else 0
    total_cart_items = len(items) if items else 0

    return {
        'items': items,
        'order_total': order_total,
        'total_cart_items': total_cart_items,
    }
def wishlist_count(request):
    count = 0
    if request.user.is_authenticated:
        count = Wishlist.objects.filter(user=request.user).count()
    return {'wishlist_count': count}