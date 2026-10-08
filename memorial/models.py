from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import decimal


class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'Buyer / Family'),
        ('admin', 'Mortuary Administrator'),
    )
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    phone = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def is_administrator(self):
        return self.role == 'admin' or self.is_superuser or self.is_staff

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.email})"


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    line1 = models.CharField(max_length=200)
    line2 = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='United States')
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.line1}, {self.city}, {self.state} {self.postal_code}"


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    DISPATCH_CHOICES = (
        ('ready', 'Immediate Crypt Dispatch (< 24h)'),
        ('bespoke', 'Artisan Atelier Handcraft'),
    )

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    material = models.CharField(max_length=100, blank=True, null=True)
    length = models.CharField(max_length=100, blank=True, null=True)
    width = models.CharField(max_length=100, blank=True, null=True)
    height = models.CharField(max_length=100, blank=True, null=True)
    finish = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    fabric = models.CharField(max_length=100, blank=True, null=True)
    sealing_system = models.CharField(max_length=100, blank=True, null=True)
    capacity = models.CharField(max_length=100, blank=True, null=True)
    dispatch_type = models.CharField(max_length=50, choices=DISPATCH_CHOICES, default='ready')
    provenance_code = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def primary_image_url(self):
        first_img = self.images.first()
        if first_img:
            return first_img.image_url
        return 'https://lh3.googleusercontent.com/aida-public/AB6AXuCBi8k5J9jpxSrq6_Ig5-qZww3t3WrZ2gCIGvUvgQeVzcjgsS1XkffTjHSYWGNzIWKwY2Id2mX2gtd8sKomhJuINTviUuc7TlVmLKHNgn0cVUrKlL_0duld9XRJrE55Pzec7xwU_U4bDpikodDfMB6HRgInIAjZTxXNjuJ94R6YQPe4xpTux-qXMpbNT-Zpx4vPjsdP3vgnolkGnIWXDdww5xOE_QUHhuD7Hb0rj6tvyyI6wV-3QTu8'

    def proportions_display(self):
        return f"{self.length}L × {self.width}W × {self.height}H"

    def __str__(self):
        return f"{self.name} (${self.price})"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image_url = models.CharField(max_length=500)

    def __str__(self):
        return f"Image for {self.product.name}"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def total_amount(self):
        return sum(item.subtotal() for item in self.items.all())

    def item_count(self):
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        return f"Cart of {self.user.email}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')

    def subtotal(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"


class Order(models.Model):
    STATUS_CHOICES = (
        ('placed', 'Order Placed & Notified'),
        ('confirmed', 'Confirmed & Crypt Vault Reserved'),
        ('dispatched', 'White-Glove Dispatched to Mortuary'),
        ('delivered', 'Directly Received by Mortuary'),
        ('cancelled', 'Order Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='placed')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    mortuary_name = models.CharField(max_length=200, blank=True, null=True)
    mortuary_director = models.CharField(max_length=150, blank=True, null=True)
    mortuary_phone = models.CharField(max_length=50, blank=True, null=True)
    delivery_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.email} - ${self.total_amount}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.quantity}x {self.product.name} (Order #{self.order.id})"


class Payment(models.Model):
    STATUS_CHOICES = (
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    method = models.CharField(max_length=50)
    transaction_ref = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment {self.status} for Order #{self.order.id}"


class Invoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=100, unique=True)
    invoice_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='PAID')

    def __str__(self):
        return f"Invoice {self.invoice_number}"


class Enquiry(models.Model):
    STATUS_CHOICES = (
        ('Open', 'Open'),
        ('Responded', 'Responded'),
        ('Closed', 'Closed'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='enquiries')
    name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    mortuary_location = models.CharField(max_length=200, blank=True, null=True)
    urgency_level = models.CharField(max_length=50, default='<24h')
    custom_type = models.CharField(max_length=100, default='Immediate Dispatch')
    message = models.TextField()
    admin_response = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Enquiries'

    def tracking_id(self):
        return f"ENQ-{self.id:04d}"

    def __str__(self):
        return f"Enquiry #{self.id} from {self.name or self.email}"


class AuthenticityCertificate(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='certificate')
    verification_code = models.CharField(max_length=50, unique=True)
    qr_code_url = models.CharField(max_length=500, blank=True, null=True)
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='issued_certificates')
    issued_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Certificate {self.verification_code} ({self.product.name})"


class SystemSetting(models.Model):
    setting_key = models.CharField(max_length=100, unique=True)
    setting_value = models.TextField(blank=True, null=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.setting_key}: {self.setting_value}"
