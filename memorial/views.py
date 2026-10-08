from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Count, Sum
from decimal import Decimal
import uuid
import datetime
from django.utils import timezone

from .models import (
    User, Address, Category, Product, ProductImage, Cart, CartItem,
    Order, OrderItem, Payment, Invoice, Enquiry,
    AuthenticityCertificate, SystemSetting
)
from .forms import (
    UserRegistrationForm, UserLoginForm, CheckoutForm,
    UrgentEnquiryForm, ProductForm
)


def is_admin(user):
    return user.is_authenticated and (user.role == 'admin' or user.is_staff or user.is_superuser)


# --- Public Navigation Views ---

def home_view(request):
    featured_products = Product.objects.filter(is_active=True)[:4]
    categories = Category.objects.filter(is_active=True)
    return render(request, 'memorial/home.html', {
        'featured_products': featured_products,
        'categories': categories,
    })


def catalog_view(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)

    # Search query
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(material__icontains=query) |
            Q(description__icontains=query) |
            Q(finish__icontains=query)
        )

    # Category filter
    category_slug = request.GET.get('category', 'all')
    if category_slug and category_slug != 'all':
        if category_slug == 'hardwood':
            products = products.filter(category__id=1)
        elif category_slug == 'metal':
            products = products.filter(category__id=2)
        elif category_slug == 'eco':
            products = products.filter(category__id=3)
        elif category_slug == 'artisanal':
            products = products.filter(category__id=4)
        else:
            products = products.filter(category__slug=category_slug)

    # Price filter
    price_tier = request.GET.get('price', 'all')
    if price_tier == 'tier1':
        products = products.filter(price__gte=1000, price__lte=2500)
    elif price_tier == 'tier2':
        products = products.filter(price__gt=2500, price__lte=4000)
    elif price_tier == 'tier3':
        products = products.filter(price__gt=4000)

    # Fabric filter
    fabric = request.GET.get('fabric', 'all')
    if fabric and fabric != 'all':
        products = products.filter(fabric__iexact=fabric)

    # Finish filter
    finish = request.GET.get('finish', 'all')
    if finish and finish != 'all':
        products = products.filter(finish__iexact=finish)

    # Dispatch filter
    dispatch = request.GET.get('dispatch', 'all')
    if dispatch and dispatch != 'all':
        products = products.filter(dispatch_type=dispatch)

    # Sorting
    sort_by = request.GET.get('sort', 'featured')
    if sort_by == 'price-asc':
        products = products.order_by('price')
    elif sort_by == 'price-desc' or sort_by == 'purity':
        products = products.order_by('-price')
    else:
        products = products.order_by('id')

    return render(request, 'memorial/catalog.html', {
        'products': products,
        'categories': categories,
        'selected_category': category_slug,
        'selected_price': price_tier,
        'selected_fabric': fabric,
        'selected_finish': finish,
        'selected_dispatch': dispatch,
        'selected_sort': sort_by,
        'search_query': query,
        'match_count': products.count(),
    })


def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    certificate = getattr(product, 'certificate', None)
    related_products = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:3]

    return render(request, 'memorial/product_detail.html', {
        'product': product,
        'certificate': certificate,
        'related_products': related_products,
    })


# --- Shopping Cart Management ---

def cart_view(request):
    cart_items = []
    total = Decimal('0.00')

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.items.select_related('product').all()
        total = cart.total_amount()
    else:
        session_cart = request.session.get('guest_cart', {})
        for prod_id, qty in session_cart.items():
            try:
                prod = Product.objects.get(id=prod_id, is_active=True)
                subtotal = prod.price * qty
                cart_items.append({
                    'product': prod,
                    'quantity': qty,
                    'subtotal': subtotal,
                    'is_session': True,
                    'id': prod.id,
                })
                total += subtotal
            except Product.DoesNotExist:
                pass

    return render(request, 'memorial/cart.html', {
        'cart_items': cart_items,
        'total_amount': total,
    })


def cart_add_view(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    qty = int(request.POST.get('quantity', 1))

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += qty
            item.save()
        else:
            item.quantity = qty
            item.save()
    else:
        session_cart = request.session.get('guest_cart', {})
        str_id = str(product_id)
        session_cart[str_id] = session_cart.get(str_id, 0) + qty
        request.session['guest_cart'] = session_cart
        request.session.modified = True

    messages.success(request, f'"{product.name}" placed into memorial cart.')
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'cart'
    return redirect(next_url)


def cart_update_view(request, item_id):
    qty = int(request.POST.get('quantity', 1))

    if request.user.is_authenticated:
        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
            if qty <= 0:
                item.delete()
                messages.info(request, 'Item removed from memorial cart.')
            else:
                item.quantity = qty
                item.save()
                messages.success(request, 'Cart quantity updated.')
        except CartItem.DoesNotExist:
            pass
    else:
        session_cart = request.session.get('guest_cart', {})
        str_id = str(item_id)
        if str_id in session_cart:
            if qty <= 0:
                del session_cart[str_id]
                messages.info(request, 'Item removed from memorial cart.')
            else:
                session_cart[str_id] = qty
                messages.success(request, 'Cart quantity updated.')
            request.session['guest_cart'] = session_cart
            request.session.modified = True

    return redirect('cart')


def cart_remove_view(request, item_id):
    if request.user.is_authenticated:
        CartItem.objects.filter(id=item_id, cart__user=request.user).delete()
    else:
        session_cart = request.session.get('guest_cart', {})
        str_id = str(item_id)
        if str_id in session_cart:
            del session_cart[str_id]
            request.session['guest_cart'] = session_cart
            request.session.modified = True

    messages.info(request, 'Item removed from memorial cart.')
    return redirect('cart')


def cart_clear_view(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
        except Cart.DoesNotExist:
            pass
    else:
        request.session['guest_cart'] = {}
        request.session.modified = True

    messages.info(request, 'Cart emptied.')
    return redirect('cart')


# --- Checkout & Order Processing ---

@login_required(login_url='login')
def checkout_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').all()

    if not items.exists():
        messages.warning(request, 'Your cart is empty. Please select a memorial casket first.')
        return redirect('catalog')

    total_amount = cart.total_amount()

    # Pre-fill address if available
    default_address = request.user.addresses.filter(is_default=True).first() or request.user.addresses.first()
    initial_data = {}
    if default_address:
        initial_data = {
            'line1': default_address.line1,
            'line2': default_address.line2,
            'city': default_address.city,
            'state': default_address.state,
            'postal_code': default_address.postal_code,
        }

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # 1. Save Address
                address = Address.objects.create(
                    user=request.user,
                    line1=form.cleaned_data['line1'],
                    line2=form.cleaned_data.get('line2'),
                    city=form.cleaned_data['city'],
                    state=form.cleaned_data['state'],
                    postal_code=form.cleaned_data['postal_code'],
                    country='United States',
                    is_default=False
                )

                # 2. Create Order
                order = Order.objects.create(
                    user=request.user,
                    shipping_address=address,
                    status='confirmed',
                    total_amount=total_amount,
                    mortuary_name=form.cleaned_data['mortuary_name'],
                    mortuary_director=form.cleaned_data.get('mortuary_director'),
                    mortuary_phone=form.cleaned_data['mortuary_phone'],
                    delivery_notes=form.cleaned_data.get('delivery_notes')
                )

                # 3. Create OrderItems & decrement stock
                for cart_item in items:
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        unit_price=cart_item.product.price
                    )
                    cart_item.product.stock = max(0, cart_item.product.stock - cart_item.quantity)
                    cart_item.product.save()

                # 4. Create Payment
                txn_ref = f"TXN-ETR-{uuid.uuid4().hex[:8].upper()}"
                Payment.objects.create(
                    order=order,
                    method=form.cleaned_data['payment_method'],
                    transaction_ref=txn_ref,
                    status='success',
                    paid_at=timezone.now()
                )

                # 5. Create Invoice
                inv_num = f"INV-{timezone.now().year}-{order.id:04d}"
                Invoice.objects.create(
                    order=order,
                    invoice_number=inv_num,
                    total_amount=total_amount,
                    status='PAID'
                )

                # 6. Clear Cart
                cart.items.all().delete()

            messages.success(request, f'Order placed successfully! Order #{order.id}')
            return redirect('order_confirmation', order_id=order.id)
    else:
        form = CheckoutForm(initial=initial_data)

    return render(request, 'memorial/checkout.html', {
        'form': form,
        'cart_items': items,
        'total_amount': total_amount,
    })


@login_required(login_url='login')
def order_confirmation_view(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if not request.user.is_administrator() and order.user != request.user:
        return redirect('home')

    return render(request, 'memorial/order_confirmation.html', {
        'order': order,
    })


@login_required(login_url='login')
def order_list_view(request):
    if request.user.is_administrator():
        orders = Order.objects.all().order_by('-created_at')
    else:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'memorial/order_list.html', {
        'orders': orders,
    })


@login_required(login_url='login')
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if not request.user.is_administrator() and order.user != request.user:
        return redirect('home')

    return render(request, 'memorial/order_detail.html', {
        'order': order,
    })


# --- Urgent Enquiries & Bespoke Services ---

def urgent_enquiry_view(request):
    if request.method == 'POST':
        form = UrgentEnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save(commit=False)
            if request.user.is_authenticated:
                enquiry.user = request.user
            enquiry.save()
            messages.success(
                request,
                f"Urgent enquiry {enquiry.tracking_id()} received. A senior bereavement counselor has been dispatched to coordinate."
            )
            return redirect('urgent_enquiry_success', enquiry_id=enquiry.id)
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
                'phone': request.user.phone,
            }
        form = UrgentEnquiryForm(initial=initial)

    user_enquiries = []
    if request.user.is_authenticated:
        user_enquiries = Enquiry.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'memorial/urgent_enquiry.html', {
        'form': form,
        'user_enquiries': user_enquiries,
    })


def urgent_enquiry_success_view(request, enquiry_id):
    enquiry = get_object_or_404(Enquiry, pk=enquiry_id)
    return render(request, 'memorial/urgent_enquiry_success.html', {
        'enquiry': enquiry,
    })


# --- Authenticity Certificates ---

def certificate_verify_view(request):
    code = request.GET.get('code', '').strip()
    certificate = None
    not_found = False

    if code:
        try:
            certificate = AuthenticityCertificate.objects.select_related('product', 'issued_by').get(verification_code__iexact=code)
        except AuthenticityCertificate.DoesNotExist:
            not_found = True

    return render(request, 'memorial/certificate_verify.html', {
        'search_code': code,
        'certificate': certificate,
        'not_found': not_found,
    })


# --- About, Guidance & FAQ ---

def about_view(request):
    return render(request, 'memorial/about.html')


def faq_view(request):
    return render(request, 'memorial/faq.html')


# --- User Authentication & Profile ---

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email'].split('@')[0] + uuid.uuid4().hex[:4]
            user.set_password(form.cleaned_data['password'])
            user.role = 'user'
            user.save()

            # Create Cart
            Cart.objects.get_or_create(user=user)

            # Sync guest session cart to user cart
            session_cart = request.session.get('guest_cart', {})
            if session_cart:
                cart = user.cart
                for prod_id, qty in session_cart.items():
                    try:
                        p = Product.objects.get(id=prod_id)
                        ci, created = CartItem.objects.get_or_create(cart=cart, product=p)
                        ci.quantity = ci.quantity + qty if not created else qty
                        ci.save()
                    except Product.DoesNotExist:
                        pass
                request.session['guest_cart'] = {}

            login(request, user)
            messages.success(request, f'Welcome to Eternum, {user.first_name or user.username}.')
            return redirect('home')
    else:
        form = UserRegistrationForm()

    return render(request, 'memorial/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        user = authenticate(request, email=email, password=password)
        if not user:
            # Fallback for username login
            try:
                user_obj = User.objects.get(email__iexact=email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user:
            if not user.is_active:
                messages.error(request, 'This account is deactivated.')
            else:
                login(request, user)
                Cart.objects.get_or_create(user=user)

                # Sync guest session cart
                session_cart = request.session.get('guest_cart', {})
                if session_cart:
                    cart = user.cart
                    for prod_id, qty in session_cart.items():
                        try:
                            p = Product.objects.get(id=prod_id)
                            ci, created = CartItem.objects.get_or_create(cart=cart, product=p)
                            ci.quantity = ci.quantity + qty if not created else qty
                            ci.save()
                        except Product.DoesNotExist:
                            pass
                    request.session['guest_cart'] = {}

                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}.')
                next_url = request.GET.get('next') or ('admin_dashboard' if user.is_administrator() else 'home')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'memorial/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required(login_url='login')
def profile_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    enquiries = Enquiry.objects.filter(user=request.user).order_by('-created_at')
    addresses = request.user.addresses.all()

    if request.method == 'POST' and 'update_profile' in request.POST:
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name = request.POST.get('last_name', request.user.last_name)
        request.user.phone = request.POST.get('phone', request.user.phone)
        request.user.save()
        messages.success(request, 'Profile details updated.')
        return redirect('profile')

    return render(request, 'memorial/profile.html', {
        'orders': orders,
        'enquiries': enquiries,
        'addresses': addresses,
    })


# --- Admin Portal (Solemn Modern Gothic Admin View) ---

@user_passes_test(is_admin, login_url='login')
def admin_dashboard_view(request):
    total_revenue = Order.objects.filter(status__in=['confirmed', 'dispatched', 'delivered']).aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')
    total_orders = Order.objects.count()
    open_enquiries_count = Enquiry.objects.filter(status='Open').count()
    products_count = Product.objects.filter(is_active=True).count()

    recent_orders = Order.objects.all().order_by('-created_at')[:8]
    recent_enquiries = Enquiry.objects.all().order_by('-created_at')[:6]
    all_products = Product.objects.all().order_by('-id')
    certificates = AuthenticityCertificate.objects.all().order_by('-issued_at')[:8]

    # Handle actions
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_order_status':
            order_id = request.POST.get('order_id')
            new_status = request.POST.get('status')
            order = get_object_or_404(Order, pk=order_id)
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.id} status updated to {order.get_status_display()}')
            return redirect('admin_dashboard')

        elif action == 'respond_enquiry':
            enquiry_id = request.POST.get('enquiry_id')
            counselor_note = request.POST.get('admin_response')
            new_status = request.POST.get('status', 'Responded')
            enquiry = get_object_or_404(Enquiry, pk=enquiry_id)
            enquiry.admin_response = counselor_note
            enquiry.status = new_status
            enquiry.save()
            messages.success(request, f'Response recorded for Enquiry {enquiry.tracking_id()}')
            return redirect('admin_dashboard')

        elif action == 'add_product':
            form = ProductForm(request.POST)
            if form.is_valid():
                p = form.save(commit=False)
                prov_code = f"ETR-AUTH-{uuid.uuid4().hex[:4].upper()}"
                p.provenance_code = prov_code
                p.save()
                img_url = form.cleaned_data.get('image_url') or 'https://lh3.googleusercontent.com/aida-public/AB6AXuCBi8k5J9jpxSrq6_Ig5-qZww3t3WrZ2gCIGvUvgQeVzcjgsS1XkffTjHSYWGNzIWKwY2Id2mX2gtd8sKomhJuINTviUuc7TlVmLKHNgn0cVUrKlL_0duld9XRJrE55Pzec7xwU_U4bDpikodDfMB6HRgInIAjZTxXNjuJ94R6YQPe4xpTux-qXMpbNT-Zpx4vPjsdP3vgnolkGnIWXDdww5xOE_QUHhuD7Hb0rj6tvyyI6wV-3QTu8'
                ProductImage.objects.create(product=p, image_url=img_url)
                AuthenticityCertificate.objects.create(
                    product=p,
                    verification_code=prov_code,
                    qr_code_url=f'https://api.qrserver.com/v1/create-qr-code/?size=160x160&data={prov_code}',
                    issued_by=request.user,
                    is_active=True
                )
                messages.success(request, f'New casket "{p.name}" added with provenance code {prov_code}')
                return redirect('admin_dashboard')

        elif action == 'toggle_product':
            p_id = request.POST.get('product_id')
            p = get_object_or_404(Product, pk=p_id)
            p.is_active = not p.is_active
            p.save()
            messages.info(request, f'Product "{p.name}" active status: {p.is_active}')
            return redirect('admin_dashboard')

    product_form = ProductForm()

    return render(request, 'memorial/admin_dashboard.html', {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'open_enquiries_count': open_enquiries_count,
        'products_count': products_count,
        'recent_orders': recent_orders,
        'recent_enquiries': recent_enquiries,
        'all_products': all_products,
        'certificates': certificates,
        'product_form': product_form,
    })
