from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Address, Category, Product, ProductImage, Cart, CartItem,
    Order, OrderItem, Payment, Invoice, Enquiry,
    AuthenticityCertificate, SystemSetting
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class AuthenticityCertificateInline(admin.StackedInline):
    model = AuthenticityCertificate
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'material', 'finish', 'dispatch_type', 'is_active')
    list_filter = ('category', 'dispatch_type', 'is_active', 'finish', 'fabric')
    search_fields = ('name', 'material', 'description', 'provenance_code')
    inlines = [ProductImageInline, AuthenticityCertificateInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    prepopulated_fields = {'slug': ('name',)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'mortuary_name', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'user__email', 'mortuary_name', 'mortuary_director', 'mortuary_phone')
    inlines = [OrderItemInline]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'order', 'total_amount', 'status', 'invoice_date')
    search_fields = ('invoice_number', 'order__id')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'method', 'transaction_ref', 'status', 'paid_at')
    list_filter = ('status', 'method')


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'urgency_level', 'custom_type', 'status', 'created_at')
    list_filter = ('status', 'urgency_level')
    search_fields = ('name', 'email', 'phone', 'message', 'mortuary_location')


@admin.register(AuthenticityCertificate)
class AuthenticityCertificateAdmin(admin.ModelAdmin):
    list_display = ('verification_code', 'product', 'issued_by', 'issued_at', 'is_active')
    search_fields = ('verification_code', 'product__name')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'line1', 'city', 'state', 'postal_code', 'is_default')
    search_fields = ('user__email', 'line1', 'city', 'postal_code')


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('setting_key', 'setting_value', 'updated_at')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Eternum Role & Contact', {'fields': ('role', 'phone')}),
    )
    list_display = ('email', 'username', 'first_name', 'last_name', 'role', 'phone', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone')
