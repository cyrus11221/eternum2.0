from django.test import TestCase, Client
from django.urls import reverse
from memorial.models import User, Category, Product, AuthenticityCertificate, Order, Enquiry
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
        self.category = Category.objects.create(name='Solid Hardwood Sanctuary', slug='hardwood')
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
        self.assertContains(response, 'A Dignified Choice for Every Family')
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
        self.assertContains(cart_res, '$2850.00')

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
        self.assertContains(response, 'Certificate of Provenance &amp; Sealing')
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
            'delivery_notes': 'Please call 30 mins prior to delivery.',
            'payment_method': 'Sandbox Card'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Order.objects.filter(user=self.buyer).exists())

    def test_admin_portal_access(self):
        self.client.login(username='admin@eternum.com', password='admin123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Eternum Central Director Portal')
