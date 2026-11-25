from io import BytesIO
from tempfile import TemporaryDirectory
from django.test import TestCase, Client
from django.test.utils import override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.deletion import ProtectedError
from PIL import Image
from memorial.models import User, Category, Product, AuthenticityCertificate, Order, OrderItem, Enquiry, Cart, CartItem
from decimal import Decimal


class EternumSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='admin_test',
            email='admin@eternum.com',
            password='admin123',
            role='admin',
            first_name='Admin',
            last_name='Director'
        )
        self.buyer = User.objects.create_user(
            username='buyer_test',
            email='eleanor@example.com',
            password='user123',
            role='user',
            first_name='Eleanor',
            last_name='Vance'
        )
        self.category = Category.objects.create(name='Hardwood Caskets', slug='hardwood')
        self.product = Product.objects.create(
            category=self.category,
            name='The Westminster Solid Oak',
            description='White oak with warm satin finish.',
            material='American White Oak',
            length='82″',
            width='28″',
            height='23″',
            finish='satin',
            price=Decimal('2850.00'),
            stock=5,
            fabric='crepe',
            sealing_system='Master Joinery Lock',
            capacity='350 lbs',
            dispatch_type='ready',
            provenance_code='ETR-AUTH-0824',
            is_active=True
        )
        self.certificate = AuthenticityCertificate.objects.create(
            product=self.product,
            verification_code='ETR-AUTH-0824',
            qr_code_url='https://example.com/qr.png',
            issued_by=self.admin,
            is_active=True
        )

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Memorial Products for Every Family')
        self.assertContains(response, 'The Westminster Solid Oak')

    def test_catalog_and_filtering(self):
        response = self.client.get(reverse('catalog'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The Westminster Solid Oak')

        # Filter by category
        res_cat = self.client.get(reverse('catalog'), {'category': 'hardwood'})
        self.assertEqual(res_cat.status_code, 200)
        self.assertContains(res_cat, 'The Westminster Solid Oak')

        # Search
        res_search = self.client.get(reverse('catalog'), {'q': 'Westminster'})
        self.assertEqual(res_search.status_code, 200)
        self.assertContains(res_search, 'The Westminster Solid Oak')

    def test_product_detail(self):
        response = self.client.get(reverse('product_detail', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'American White Oak')
        self.assertContains(response, 'ETR-AUTH-0824')

    def test_cart_operations(self):
        # Add to cart as guest
        response = self.client.post(reverse('cart_add', args=[self.product.id]), {'quantity': 1}, follow=True)
        self.assertEqual(response.status_code, 200)
        cart_res = self.client.get(reverse('cart'))
        self.assertContains(cart_res, 'The Westminster Solid Oak')
        self.assertContains(cart_res, '₹2850.00')

    def test_urgent_enquiry_submission(self):
        response = self.client.post(reverse('urgent_enquiry'), {
            'name': 'Eleanor Vance',
            'email': 'eleanor@example.com',
            'phone': '+1 (555) 234-5678',
            'mortuary_location': 'Portland Chapel',
            'urgency_level': '<24h',
            'custom_type': 'Immediate Dispatch',
            'message': 'Need priority direct transport for tomorrow.'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Enquiry.objects.filter(email='eleanor@example.com').exists())

    def test_certificate_verification(self):
        response = self.client.get(reverse('certificate_verify'), {'code': 'ETR-AUTH-0824'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Product Certificate')
        self.assertContains(response, 'The Westminster Solid Oak')

    def test_authenticated_checkout(self):
        self.client.login(username='eleanor@example.com', password='user123')
        # Add item to user cart
        self.client.post(reverse('cart_add', args=[self.product.id]), {'quantity': 1})
        # Checkout
        response = self.client.post(reverse('checkout'), {
            'mortuary_name': 'Graceview Memorial Sanctuary',
            'mortuary_director': 'Director Robert Sterling',
            'mortuary_phone': '+1 (555) 890-1234',
            'line1': '742 Evergreen Terrace',
            'line2': 'Bay 2',
            'city': 'Portland',
            'state': 'OR',
            'postal_code': '97201',
            'country': 'United States',
            'delivery_notes': 'Please call 30 mins prior to delivery.',
            'payment_method': 'Sandbox Card'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Order.objects.filter(user=self.buyer).exists())
        self.assertEqual(Order.objects.get(user=self.buyer).shipping_address.country, 'United States')

    def test_checkout_rejects_invalid_address(self):
        self.client.login(username='eleanor@example.com', password='user123')
        self.client.post(reverse('cart_add', args=[self.product.id]), {'quantity': 1})

        response = self.client.post(reverse('checkout'), {
            'mortuary_name': 'Graceview Memorial Sanctuary',
            'mortuary_phone': '+1 (555) 890-1234',
            'line1': '742 Evergreen Terrace',
            'city': 'Portland',
            'state': 'OR',
            'postal_code': '!!!',
            'country': 'United States',
            'payment_method': 'Sandbox Card',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a valid postal code')
        self.assertFalse(Order.objects.filter(user=self.buyer).exists())
        self.assertFalse(self.buyer.addresses.exists())

    def test_checkout_rejects_blank_address(self):
        self.client.login(username='eleanor@example.com', password='user123')
        self.client.post(reverse('cart_add', args=[self.product.id]), {'quantity': 1})

        response = self.client.post(reverse('checkout'), {
            'mortuary_name': 'Graceview Memorial Sanctuary',
            'mortuary_phone': '+1 (555) 890-1234',
            'line1': '',
            'city': '',
            'state': '',
            'postal_code': '',
            'country': '',
            'payment_method': 'Sandbox Card',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        self.assertFalse(Order.objects.filter(user=self.buyer).exists())
        self.assertFalse(self.buyer.addresses.exists())

    def test_admin_portal_access(self):
        self.client.login(username='admin@eternum.com', password='admin123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Eternum Central Director Portal')

    def test_admin_can_add_product_from_inventory(self):
        self.client.login(username='admin@eternum.com', password='admin123')

        inventory_response = self.client.get(reverse('admin_dashboard'), {'tab': 'inventory'})
        self.assertContains(inventory_response, 'Add Product')
        self.assertContains(inventory_response, 'id="add-product"')
        self.assertContains(inventory_response, 'id="delete-product-dialog"')
        self.assertNotContains(inventory_response, 'onsubmit="return confirm(')

        response = self.client.post(reverse('admin_dashboard'), {
            'action': 'add_product',
            'name': 'The Cedar Memorial',
            'category': self.category.id,
            'price': '24000.00',
            'stock': '3',
            'dispatch_type': 'ready',
            'material': 'Cedar',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        product = Product.objects.get(name='The Cedar Memorial')
        self.assertTrue(AuthenticityCertificate.objects.filter(product=product).exists())

    def test_admin_can_delete_product_with_themed_toast(self):
        self.client.login(username='admin@eternum.com', password='admin123')

        response = self.client.post(reverse('admin_dashboard'), {
            'action': 'delete_product',
            'product_id': self.product.id,
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())
        self.assertContains(response, 'data-toast')
        self.assertContains(response, 'was removed from the catalog.')

    def test_admin_can_upload_product_image(self):
        self.client.login(username='admin@eternum.com', password='admin123')
        image_buffer = BytesIO()
        Image.new('RGB', (2, 2), color='navy').save(image_buffer, format='PNG')
        upload = SimpleUploadedFile(
            'cedar-memorial.png',
            image_buffer.getvalue(),
            content_type='image/png',
        )

        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            response = self.client.post(reverse('admin_dashboard'), {
                'action': 'add_product',
                'name': 'The Uploaded Cedar Memorial',
                'category': self.category.id,
                'price': '24000.00',
                'stock': '3',
                'dispatch_type': 'ready',
                'material': 'Cedar',
                'image_file': upload,
            }, follow=True)

            self.assertEqual(response.status_code, 200)
            product = Product.objects.get(name='The Uploaded Cedar Memorial')
            product_image = product.images.get()
            self.assertTrue(product_image.image)
            self.assertTrue(product_image.image.storage.exists(product_image.image.name))
            self.assertEqual(product.primary_image_url(), product_image.image.url)
            self.assertTrue(product.primary_image_url().startswith('/media/products/'))

    def test_admin_rejects_non_image_product_upload(self):
        self.client.login(username='admin@eternum.com', password='admin123')
        upload = SimpleUploadedFile(
            'not-an-image.png',
            b'not an image',
            content_type='image/png',
        )

        response = self.client.post(reverse('admin_dashboard'), {
            'action': 'add_product',
            'name': 'Invalid Image Product',
            'category': self.category.id,
            'price': '24000.00',
            'stock': '3',
            'dispatch_type': 'ready',
            'image_file': upload,
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Product.objects.filter(name='Invalid Image Product').exists())

    def test_login_and_register_include_password_visibility_toggle(self):
        login_response = self.client.get(reverse('login'))
        self.assertEqual(login_response.status_code, 200)
        self.assertContains(login_response, '<div class="relative" data-password-field>', count=1)
        self.assertContains(login_response, 'data-password-toggle-icon>visibility</span>', count=1)
        self.assertContains(login_response, 'aria-label="Show password"', count=1)
        self.assertContains(login_response, 'pr-11', count=1)

        register_response = self.client.get(reverse('register'))
        self.assertEqual(register_response.status_code, 200)
        self.assertContains(register_response, '<div class="relative" data-password-field>', count=2)
        self.assertContains(register_response, 'data-password-toggle-icon>visibility</span>', count=2)
        self.assertContains(register_response, 'aria-label="Show password"', count=1)
        self.assertContains(register_response, 'aria-label="Show confirm password"', count=1)
        self.assertContains(register_response, 'pr-11', count=2)

    def test_newly_created_products_are_available_by_default(self):
        created = Product.objects.create(
            category=self.category,
            name='The Default Available Oak',
            price=Decimal('3100.00'),
            stock=2,
        )
        self.assertTrue(created.is_available)
        self.assertTrue(self.product.is_available)

        self.client.login(username='admin@eternum.com', password='admin123')
        response = self.client.post(reverse('admin_dashboard'), {
            'action': 'add_product',
            'name': 'The Admin Created Elm',
            'category': self.category.id,
            'price': '2750.00',
            'stock': '4',
            'dispatch_type': 'ready',
            'material': 'Elm',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        admin_created = Product.objects.get(name='The Admin Created Elm')
        self.assertTrue(admin_created.is_available)
        self.assertContains(response, 'Available')
        self.assertContains(response, 'Mark Unavailable')

    def test_admin_can_toggle_availability_and_storefront_displays_out_of_stock(self):
        self.client.login(username='admin@eternum.com', password='admin123')

        # Mark product unavailable
        toggle_off = self.client.post(reverse('admin_dashboard'), {
            'action': 'toggle_availability',
            'product_id': self.product.id,
        }, follow=True)
        self.assertEqual(toggle_off.status_code, 200)
        self.product.refresh_from_db()
        self.assertFalse(self.product.is_available)
        self.assertContains(toggle_off, 'Unavailable')
        self.assertContains(toggle_off, 'Mark Available')

        # Storefront pages keep product visible with Out of Stock label and disabled Add to Cart
        self.client.logout()
        for url in [
            reverse('home'),
            reverse('catalog'),
            reverse('product_detail', args=[self.product.id]),
        ]:
            page = self.client.get(url)
            self.assertEqual(page.status_code, 200)
            self.assertContains(page, self.product.name)
            self.assertContains(page, 'Out of Stock')
            self.assertContains(page, 'disabled aria-disabled="true"')

        # Admin reactivates product
        self.client.login(username='admin@eternum.com', password='admin123')
        toggle_on = self.client.post(reverse('admin_dashboard'), {
            'action': 'toggle_availability',
            'product_id': self.product.id,
        }, follow=True)
        self.assertEqual(toggle_on.status_code, 200)
        self.product.refresh_from_db()
        self.assertTrue(self.product.is_available)

        self.client.logout()
        detail_page = self.client.get(reverse('product_detail', args=[self.product.id]))
        self.assertNotContains(detail_page, 'Out of Stock')
        self.assertContains(detail_page, f'action="{reverse("cart_add", args=[self.product.id])}"')

    def test_customers_cannot_add_unavailable_product_to_cart(self):
        self.product.is_available = False
        self.product.save(update_fields=['is_available'])

        # Guest direct POST
        guest_res = self.client.post(reverse('cart_add', args=[self.product.id]), {'quantity': 1}, follow=True)
        self.assertEqual(guest_res.status_code, 200)
        self.assertContains(guest_res, 'out of stock')
        self.assertEqual(self.client.session.get('guest_cart', {}), {})

        # Authenticated direct POST
        self.client.login(username='eleanor@example.com', password='user123')
        auth_res = self.client.post(reverse('cart_add', args=[self.product.id]), {'quantity': 2}, follow=True)
        self.assertEqual(auth_res.status_code, 200)
        self.assertContains(auth_res, 'out of stock')
        self.assertFalse(CartItem.objects.filter(cart__user=self.buyer, product=self.product).exists())

    def test_checkout_rejects_product_that_became_unavailable(self):
        self.client.login(username='eleanor@example.com', password='user123')
        self.client.post(reverse('cart_add', args=[self.product.id]), {'quantity': 1})

        # Admin marks product unavailable while it's in the customer's cart
        self.product.is_available = False
        self.product.save(update_fields=['is_available'])

        cart_res = self.client.get(reverse('cart'))
        self.assertEqual(cart_res.status_code, 200)
        self.assertContains(cart_res, 'Out of Stock')

        checkout_get = self.client.get(reverse('checkout'))
        self.assertEqual(checkout_get.status_code, 200)
        self.assertContains(checkout_get, 'currently out of stock')

        # Direct POST to checkout must be rejected
        checkout_post = self.client.post(reverse('checkout'), {
            'mortuary_name': 'Graceview Memorial Sanctuary',
            'mortuary_director': 'Director Robert Sterling',
            'mortuary_phone': '+1 (555) 890-1234',
            'line1': '742 Evergreen Terrace',
            'city': 'Portland',
            'state': 'OR',
            'postal_code': '97201',
            'country': 'United States',
            'payment_method': 'Sandbox Card',
        })
        self.assertEqual(checkout_post.status_code, 200)
        self.assertContains(checkout_post, 'Checkout cannot proceed')
        self.assertFalse(Order.objects.filter(user=self.buyer).exists())

    def test_existing_orders_remain_accessible_and_product_deletion_is_protected(self):
        self.client.login(username='eleanor@example.com', password='user123')
        self.client.post(reverse('cart_add', args=[self.product.id]), {'quantity': 2})
        self.client.post(reverse('checkout'), {
            'mortuary_name': 'Graceview Memorial Sanctuary',
            'mortuary_phone': '+1 (555) 890-1234',
            'line1': '742 Evergreen Terrace',
            'city': 'Portland',
            'state': 'OR',
            'postal_code': '97201',
            'country': 'United States',
            'payment_method': 'Sandbox Card',
        })
        order = Order.objects.get(user=self.buyer)
        order_item = order.items.get()
        self.assertEqual(order_item.product_name, 'The Westminster Solid Oak')
        self.assertEqual(order_item.unit_price, Decimal('2850.00'))
        self.assertEqual(order_item.quantity, 2)

        # Product becomes unavailable and its current price/name changes later
        self.product.is_available = False
        self.product.name = 'The Westminster Revised'
        self.product.price = Decimal('3999.00')
        self.product.save()

        # Existing order remains accessible with historical snapshot values
        order_list_res = self.client.get(reverse('order_list'))
        self.assertEqual(order_list_res.status_code, 200)
        self.assertContains(order_list_res, f'#ETR-{order.id:04d}')

        order_detail_res = self.client.get(reverse('order_detail', args=[order.id]))
        self.assertEqual(order_detail_res.status_code, 200)
        self.assertContains(order_detail_res, 'The Westminster Solid Oak')
        self.assertContains(order_detail_res, '2850.00')
        self.assertContains(order_detail_res, '5700.00')

        # ORM-level PROTECT blocks deleting products referenced by OrderItems
        with self.assertRaises(ProtectedError):
            self.product.delete()

        # Admin delete_product action also refuses deletion and preserves product
        self.client.login(username='admin@eternum.com', password='admin123')
        del_res = self.client.post(reverse('admin_dashboard'), {
            'action': 'delete_product',
            'product_id': self.product.id,
        }, follow=True)
        self.assertEqual(del_res.status_code, 200)
        self.assertContains(del_res, 'referenced by existing orders')
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())
