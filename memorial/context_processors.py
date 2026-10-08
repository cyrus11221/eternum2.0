from .models import Cart, Product

def memorial_context(request):
    cart_count = 0
    cart_total = 0.0

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = cart.item_count()
            cart_total = float(cart.total_amount())
        except Cart.DoesNotExist:
            cart_count = 0
            cart_total = 0.0
    else:
        # Session based cart for guests
        session_cart = request.session.get('guest_cart', {})
        for prod_id, qty in session_cart.items():
            cart_count += qty
            try:
                prod = Product.objects.get(id=prod_id)
                cart_total += float(prod.price) * qty
            except Product.DoesNotExist:
                pass

    return {
        'cart_count': cart_count,
        'cart_total': cart_total,
        'memorial_hotline': '1-800-ETERNUM (383-7686)',
        'site_title': 'ETERNUM — Sanctuary & Heritage',
    }
