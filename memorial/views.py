from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.conf import settings
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
    UrgentEnquiryForm, ProductForm, ProductImageUploadForm
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
        slug_map = {
            'hardwood': 'hardwood',
            'metal': 'metal',
            'eco': 'eco',
            'artisanal': 'artisanal',
        }
        target_slug = slug_map.get(category_slug, category_slug)
        products = products.filter(
            Q(category__slug__iexact=target_slug) |
            Q(category__name__icontains=target_slug) |
            Q(category__slug__icontains=target_slug)
        )

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
            'country': default_address.country,
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
                    country=form.cleaned_data['country'],
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


# --- Admin Portal (Solemn Modern Gothic Director Suite) ---

@user_passes_test(is_admin, login_url='login')
def admin_dashboard_view(request):
    """
    Central mortuary administrative operations suite:
    - Multi-tab management: overview, orders & dispatch, inventory, enquiries, certificates, settings, and users.
    - Handles status transitions, stock quick-adjustments, product commissioning, certificate issuing, and counselor notes.
    """
    # Active tab from query param
    active_tab = request.GET.get('tab', 'overview')

    # Handle POST Actions
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_order_status':
            order_id = request.POST.get('order_id')
            new_status = request.POST.get('status')
            order = get_object_or_404(Order, pk=order_id)
            order.status = new_status
            delivery_notes = request.POST.get('delivery_notes')
            if delivery_notes is not None:
                order.delivery_notes = delivery_notes
            order.save()
            messages.success(request, f'Order #ETR-{order.id:04d} status updated to {order.get_status_display()}')
            return redirect(f"{reverse('admin_dashboard')}?tab=orders")

        elif action == 'update_order_details':
            order_id = request.POST.get('order_id')
            order = get_object_or_404(Order, pk=order_id)
            order.mortuary_name = request.POST.get('mortuary_name', order.mortuary_name)
            order.mortuary_director = request.POST.get('mortuary_director', order.mortuary_director)
            order.mortuary_phone = request.POST.get('mortuary_phone', order.mortuary_phone)
            order.delivery_notes = request.POST.get('delivery_notes', order.delivery_notes)
            order.save()
            messages.success(request, f'Mortuary destination details updated for Order #ETR-{order.id:04d}.')
            return redirect(f"{reverse('admin_dashboard')}?tab=orders")

        elif action == 'add_product':
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                p = form.save(commit=False)
                prov_code = f"ETR-AUTH-{uuid.uuid4().hex[:4].upper()}"
                p.provenance_code = prov_code
                p.save()
                ProductImage.objects.create(
                    product=p,
                    image=form.cleaned_data.get('image_file'),
                    image_url=form.cleaned_data.get('image_url') or (
                        '' if form.cleaned_data.get('image_file') else
                        'https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=800&q=80'
                    ),
                )
                AuthenticityCertificate.objects.create(
                    product=p,
                    verification_code=prov_code,
                    qr_code_url=f'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={prov_code}',
                    issued_by=request.user,
                    is_active=True
                )
                messages.success(request, f'New casket "{p.name}" added to vault with code {prov_code}')
            else:
                messages.error(request, f'Error adding casket: {form.errors.as_text()}')
            return redirect(f"{reverse('admin_dashboard')}?tab=inventory")

        elif action == 'edit_product':
            image_upload_form = ProductImageUploadForm(request.FILES)
            if request.FILES.get('image_file') and not image_upload_form.is_valid():
                messages.error(request, f'Error updating product image: {image_upload_form.errors.as_text()}')
                return redirect(f"{reverse('admin_dashboard')}?tab=inventory")

            p_id = request.POST.get('product_id')
            p = get_object_or_404(Product, pk=p_id)
            p.name = request.POST.get('name', p.name).strip()
            cat_id = request.POST.get('category')
            if cat_id:
                p.category_id = cat_id
            try:
                p.price = Decimal(request.POST.get('price', p.price))
            except Exception:
                pass
            try:
                p.stock = max(0, int(request.POST.get('stock', p.stock)))
            except Exception:
                pass
            p.material = request.POST.get('material', p.material)
            p.finish = request.POST.get('finish', p.finish)
            p.fabric = request.POST.get('fabric', p.fabric)
            p.length = request.POST.get('length', p.length)
            p.width = request.POST.get('width', p.width)
            p.height = request.POST.get('height', p.height)
            p.capacity = request.POST.get('capacity', p.capacity)
            p.sealing_system = request.POST.get('sealing_system', p.sealing_system)
            p.dispatch_type = request.POST.get('dispatch_type', p.dispatch_type)
            p.description = request.POST.get('description', p.description)
            p.is_active = request.POST.get('is_active') in ['on', 'true', 'True', '1']
            p.save()

            image_url = request.POST.get('image_url', '').strip()
            uploaded_image = image_upload_form.cleaned_data.get('image_file') if request.FILES.get('image_file') else None
            first_img = p.images.first()
            if uploaded_image or image_url:
                if first_img:
                    old_image = first_img.image
                    if uploaded_image:
                        first_img.image = uploaded_image
                        first_img.image_url = ''
                    else:
                        first_img.image_url = image_url
                    first_img.save()
                    if uploaded_image and old_image:
                        old_image.delete(save=False)
                else:
                    ProductImage.objects.create(
                        product=p,
                        image=uploaded_image,
                        image_url='' if uploaded_image else image_url,
                    )

            messages.success(request, f'Vault casket "{p.name}" specifications updated.')
            return redirect(f"{reverse('admin_dashboard')}?tab=inventory")

        elif action == 'quick_stock':
            p_id = request.POST.get('product_id')
            p = get_object_or_404(Product, pk=p_id)
            delta = int(request.POST.get('delta', 0))
            p.stock = max(0, p.stock + delta)
            p.save()
            messages.success(request, f'Stock for "{p.name}" updated to {p.stock} units in vault.')
            return redirect(f"{reverse('admin_dashboard')}?tab=inventory")

        elif action == 'toggle_product':
            p_id = request.POST.get('product_id')
            p = get_object_or_404(Product, pk=p_id)
            p.is_active = not p.is_active
            p.save()
            messages.info(request, f'Product "{p.name}" active status: {p.is_active}')
            return redirect(f"{reverse('admin_dashboard')}?tab=inventory")

        elif action == 'delete_product':
            p_id = request.POST.get('product_id')
            p = get_object_or_404(Product, pk=p_id)
            name = p.name
            p.delete()
            messages.warning(request, f'Casket "{name}" removed from sanctuary catalog.')
            return redirect(f"{reverse('admin_dashboard')}?tab=inventory")

        elif action == 'respond_enquiry':
            enquiry_id = request.POST.get('enquiry_id')
            counselor_note = request.POST.get('admin_response')
            new_status = request.POST.get('status', 'Responded')
            enquiry = get_object_or_404(Enquiry, pk=enquiry_id)
            enquiry.admin_response = counselor_note
            enquiry.status = new_status
            enquiry.save()
            messages.success(request, f'Response recorded for Enquiry {enquiry.tracking_id()}')
            return redirect(f"{reverse('admin_dashboard')}?tab=enquiries")

        elif action == 'delete_enquiry':
            enquiry_id = request.POST.get('enquiry_id')
            enquiry = get_object_or_404(Enquiry, pk=enquiry_id)
            tracking = enquiry.tracking_id()
            enquiry.delete()
            messages.info(request, f'Enquiry {tracking} removed.')
            return redirect(f"{reverse('admin_dashboard')}?tab=enquiries")

        elif action == 'issue_certificate':
            p_id = request.POST.get('product_id')
            p = get_object_or_404(Product, pk=p_id)
            prov_code = p.provenance_code or f"ETR-AUTH-{uuid.uuid4().hex[:4].upper()}"
            if not p.provenance_code:
                p.provenance_code = prov_code
                p.save()
            cert, created = AuthenticityCertificate.objects.get_or_create(
                product=p,
                defaults={
                    'verification_code': prov_code,
                    'qr_code_url': f'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={prov_code}',
                    'issued_by': request.user,
                    'is_active': True
                }
            )
            if not created:
                cert.verification_code = prov_code
                cert.qr_code_url = f'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={prov_code}'
                cert.is_active = True
                cert.issued_by = request.user
                cert.save()
            messages.success(request, f'Authenticity certificate issued/refreshed for {p.name} ({prov_code})')
            return redirect(f"{reverse('admin_dashboard')}?tab=certificates")

        elif action == 'toggle_certificate':
            cert_id = request.POST.get('cert_id')
            cert = get_object_or_404(AuthenticityCertificate, pk=cert_id)
            cert.is_active = not cert.is_active
            cert.save()
            messages.info(request, f'Certificate {cert.verification_code} active status: {cert.is_active}')
            return redirect(f"{reverse('admin_dashboard')}?tab=certificates")

        elif action == 'update_system_setting':
            key = request.POST.get('setting_key', '').strip()
            val = request.POST.get('setting_value', '').strip()
            if key:
                setting, _ = SystemSetting.objects.get_or_create(setting_key=key)
                setting.setting_value = val
                setting.updated_by = request.user
                setting.save()
                messages.success(request, f'System setting "{key}" saved.')
            return redirect(f"{reverse('admin_dashboard')}?tab=settings")

        elif action == 'delete_system_setting':
            setting_id = request.POST.get('setting_id')
            setting = get_object_or_404(SystemSetting, pk=setting_id)
            key = setting.setting_key
            setting.delete()
            messages.info(request, f'Setting "{key}" removed.')
            return redirect(f"{reverse('admin_dashboard')}?tab=settings")

        elif action == 'toggle_user_role':
            u_id = request.POST.get('user_id')
            target_user = get_object_or_404(User, pk=u_id)
            if target_user == request.user:
                messages.error(request, 'You cannot modify your own administrator role.')
            else:
                if target_user.role == 'admin':
                    target_user.role = 'user'
                    target_user.is_staff = False
                else:
                    target_user.role = 'admin'
                    target_user.is_staff = True
                target_user.save()
                messages.success(request, f'User {target_user.email} role updated to {target_user.get_role_display()}.')
            return redirect(f"{reverse('admin_dashboard')}?tab=users")

        elif action == 'toggle_user_status':
            u_id = request.POST.get('user_id')
            target_user = get_object_or_404(User, pk=u_id)
            if target_user == request.user:
                messages.error(request, 'You cannot deactivate your own account.')
            else:
                target_user.is_active = not target_user.is_active
                target_user.save()
                messages.info(request, f'User account {target_user.email} active status: {target_user.is_active}.')
            return redirect(f"{reverse('admin_dashboard')}?tab=users")

    # Analytics & Metrics
    total_revenue = Order.objects.filter(status__in=['confirmed', 'dispatched', 'delivered']).aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')
    total_orders = Order.objects.count()
    placed_orders_count = Order.objects.filter(status='placed').count()
    confirmed_orders_count = Order.objects.filter(status='confirmed').count()
    dispatched_orders_count = Order.objects.filter(status='dispatched').count()
    delivered_orders_count = Order.objects.filter(status='delivered').count()
    cancelled_orders_count = Order.objects.filter(status='cancelled').count()

    open_enquiries_count = Enquiry.objects.filter(status='Open').count()
    urgent_24h_count = Enquiry.objects.filter(status='Open', urgency_level='<24h').count()

    products_count = Product.objects.filter(is_active=True).count()
    low_stock_count = Product.objects.filter(is_active=True, stock__lte=2).count()
    total_inventory_units = Product.objects.filter(is_active=True).aggregate(Sum('stock'))['stock__sum'] or 0

    registered_users_count = User.objects.count()
    admin_users_count = User.objects.filter(role='admin').count()

    # Query Filter: Orders
    order_filter_status = request.GET.get('order_status', 'all')
    order_search = request.GET.get('order_search', '').strip()
    orders_qs = Order.objects.select_related('user', 'shipping_address').prefetch_related('items__product').order_by('-created_at')

    if order_filter_status != 'all':
        orders_qs = orders_qs.filter(status=order_filter_status)
    if order_search:
        clean_search = order_search.replace('#', '').replace('ETR-', '')
        orders_qs = orders_qs.filter(
            Q(id__icontains=clean_search) |
            Q(mortuary_name__icontains=order_search) |
            Q(mortuary_director__icontains=order_search) |
            Q(user__email__icontains=order_search) |
            Q(user__first_name__icontains=order_search) |
            Q(user__last_name__icontains=order_search)
        )

    # Query Filter: Products
    prod_category = request.GET.get('prod_category', 'all')
    prod_search = request.GET.get('prod_search', '').strip()
    prod_stock = request.GET.get('prod_stock', 'all')
    products_qs = Product.objects.select_related('category', 'certificate').prefetch_related('images').order_by('-id')

    if prod_category != 'all':
        products_qs = products_qs.filter(category__id=prod_category)
    if prod_stock == 'low':
        products_qs = products_qs.filter(stock__lte=2, stock__gt=0)
    elif prod_stock == 'out':
        products_qs = products_qs.filter(stock=0)
    if prod_search:
        products_qs = products_qs.filter(
            Q(name__icontains=prod_search) |
            Q(material__icontains=prod_search) |
            Q(provenance_code__icontains=prod_search)
        )

    # Query Filter: Enquiries
    enq_status = request.GET.get('enq_status', 'all')
    enq_urgency = request.GET.get('enq_urgency', 'all')
    enquiries_qs = Enquiry.objects.select_related('user').order_by('-created_at')

    if enq_status != 'all':
        enquiries_qs = enquiries_qs.filter(status=enq_status)
    if enq_urgency != 'all':
        enquiries_qs = enquiries_qs.filter(urgency_level=enq_urgency)

    # Certificates
    cert_search = request.GET.get('cert_search', '').strip()
    certs_qs = AuthenticityCertificate.objects.select_related('product', 'issued_by').order_by('-issued_at')
    if cert_search:
        certs_qs = certs_qs.filter(
            Q(verification_code__icontains=cert_search) |
            Q(product__name__icontains=cert_search)
        )

    # Users
    users_qs = User.objects.annotate(order_count=Count('orders')).order_by('-date_joined')

    # System Settings
    settings_qs = SystemSetting.objects.select_related('updated_by').order_by('setting_key')

    # Categories for filters and forms
    categories = Category.objects.all()

    # Form
    product_form = ProductForm()

    # Database Info
    engine_raw = settings.DATABASES['default']['ENGINE']
    db_engine = 'PostgreSQL' if 'postgresql' in engine_raw else engine_raw.split('.')[-1].capitalize()
    db_name = settings.DATABASES['default']['NAME']

    return render(request, 'memorial/admin_dashboard.html', {
        'active_tab': active_tab,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'placed_orders_count': placed_orders_count,
        'confirmed_orders_count': confirmed_orders_count,
        'dispatched_orders_count': dispatched_orders_count,
        'delivered_orders_count': delivered_orders_count,
        'cancelled_orders_count': cancelled_orders_count,
        'open_enquiries_count': open_enquiries_count,
        'urgent_24h_count': urgent_24h_count,
        'products_count': products_count,
        'low_stock_count': low_stock_count,
        'total_inventory_units': total_inventory_units,
        'registered_users_count': registered_users_count,
        'admin_users_count': admin_users_count,
        'orders': orders_qs,
        'products': products_qs,
        'enquiries': enquiries_qs,
        'certificates': certs_qs,
        'users_list': users_qs,
        'system_settings': settings_qs,
        'categories': categories,
        'product_form': product_form,
        'order_filter_status': order_filter_status,
        'order_search': order_search,
        'prod_category': prod_category,
        'prod_search': prod_search,
        'prod_stock': prod_stock,
        'enq_status': enq_status,
        'enq_urgency': enq_urgency,
        'cert_search': cert_search,
        'db_engine': db_engine,
        'db_name': db_name,
    })
