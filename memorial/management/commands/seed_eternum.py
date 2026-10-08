from django.core.management.base import BaseCommand
from memorial.models import (
    User, Category, Product, ProductImage, Address,
    Cart, Order, OrderItem, Payment, Invoice, Enquiry,
    AuthenticityCertificate, SystemSetting
)
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seeds the Eternum memorial database with initial categories, products, certificates, and demo accounts'

    def handle(self, *args, **options):
        self.stdout.write('Starting Eternum seeding...')

        # 1. Admin User
        admin, created = User.objects.get_or_create(
            email='admin@eternum.com',
            defaults={
                'username': 'admin',
                'first_name': 'Bereavement',
                'last_name': 'Administrator',
                'role': 'admin',
                'phone': '1-800-383-7686',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Admin user created: admin@eternum.com / admin123'))

        # 2. Customer User
        buyer, created = User.objects.get_or_create(
            email='eleanor@example.com',
            defaults={
                'username': 'eleanor',
                'first_name': 'Eleanor',
                'last_name': 'Vance',
                'role': 'user',
                'phone': '+1 (555) 234-5678',
            }
        )
        if created:
            buyer.set_password('user123')
            buyer.save()
            Cart.objects.get_or_create(user=buyer)
            self.stdout.write(self.style.SUCCESS('Customer user created: eleanor@example.com / user123'))

        # Address for buyer
        address, _ = Address.objects.get_or_create(
            user=buyer,
            line1='742 Evergreen Terrace',
            defaults={
                'line2': 'Liaison: Graceview Mortuary Direct',
                'city': 'Portland',
                'state': 'OR',
                'postal_code': '97201',
                'country': 'United States',
                'is_default': True
            }
        )

        # 3. Categories
        cat1, _ = Category.objects.get_or_create(name='Solid Hardwood Sanctuary', defaults={'slug': 'hardwood', 'is_active': True})
        cat2, _ = Category.objects.get_or_create(name='Protective Metal Architecture', defaults={'slug': 'metal', 'is_active': True})
        cat3, _ = Category.objects.get_or_create(name='Natural Living Return', defaults={'slug': 'eco', 'is_active': True})
        cat4, _ = Category.objects.get_or_create(name='Artisanal Cathedral Craft', defaults={'slug': 'artisanal', 'is_active': True})

        # 4. Products Data
        products_data = [
            {
                'id': 1,
                'category': cat1,
                'name': 'The Westminster Solid Oak',
                'description': 'Constructed from sustainably harvested American white oak with warm satin honey seal and hand-tufted tailored pearl crepe interior bedding. Includes antique brass drop bar handles and dignified classical proportions.',
                'material': 'Solid American White Oak',
                'length': '82″',
                'width': '28″',
                'height': '23″',
                'finish': 'satin',
                'price': Decimal('2850.00'),
                'stock': 4,
                'fabric': 'crepe',
                'sealing_system': 'Master Joinery Lock',
                'capacity': 'Tested up to 350 lbs',
                'dispatch_type': 'ready',
                'provenance_code': 'ETR-AUTH-0824',
                'image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuCBi8k5J9jpxSrq6_Ig5-qZww3t3WrZ2gCIGvUvgQeVzcjgsS1XkffTjHSYWGNzIWKwY2Id2mX2gtd8sKomhJuINTviUuc7TlVmLKHNgn0cVUrKlL_0duld9XRJrE55Pzec7xwU_U4bDpikodDfMB6HRgInIAjZTxXNjuJ94R6YQPe4xpTux-qXMpbNT-Zpx4vPjsdP3vgnolkGnIWXDdww5xOE_QUHhuD7Hb0rj6tvyyI6wV-3QTu8'
            },
            {
                'id': 2,
                'category': cat2,
                'name': 'The Obsidian Nocturne Bronze',
                'description': 'Engineered with an impenetrable continuous welded seam, internal rubber gasket preservation, and hand-brushed nocturnal bronze finish. 18-gauge high-tensile steel designed for timeless preservation and dignified solemnity.',
                'material': '18-Gauge High-Tensile Steel',
                'length': '83″',
                'width': '28.5″',
                'height': '23″',
                'finish': 'bronze',
                'price': Decimal('3450.00'),
                'stock': 6,
                'fabric': 'crepe',
                'sealing_system': 'Full Gasket Hermetic Lock',
                'capacity': 'Tested up to 450 lbs',
                'dispatch_type': 'ready',
                'provenance_code': 'ETR-AUTH-0912',
                'image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuDM0IFsljflvXgITtGLWWzZRMPrDRuFEqBelq1-gPiIeX-__OTVsLqT7FVrn1AYQ0rlosEaHHxqEstpxmqWxI1dlHJBOuahDuF9hqB5QfKtI6cx3TM7nPIaJc1jikjz9olp04dMISXJetcmbY9kZKGItu2wlLoseVVYX1icenR6hlIflSDD-kqKgqUaUTO4p4dmtDQdb1TBygCq9_9oMK45DJmxsdhyXiskG5RcJNP6lMoyReQkMOF3'
            },
            {
                'id': 3,
                'category': cat3,
                'name': 'The Avalon Woven Willow',
                'description': 'Hand-braided using coppiced English willow. Free from metals, synthetic glues, or chemical lacquers. Certified by the Green Burial Council and lined with unbleached organic calico cotton and a natural straw pillow.',
                'material': 'Organic Coppiced Willow',
                'length': '78″',
                'width': '26″',
                'height': '20″',
                'finish': 'natural',
                'price': Decimal('1420.00'),
                'stock': 8,
                'fabric': 'cotton',
                'sealing_system': 'Hand-Braided Willow Ties',
                'capacity': 'Tested up to 300 lbs',
                'dispatch_type': 'ready',
                'provenance_code': 'ETR-AUTH-1033',
                'image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuDPdJZjSls9QTrTbI-K6gTgMylPCJFRlY6jEvwD0ieXRoowc-8pW3qn8jMtwlzvBTrdy6cAiHh9xZinl_GcQ9YB-_iom-X3LM3YZCoH4sZuHm0gOUsc2PbBNjDfjjEK5cCxbkwo27EjKLHRk6YSStOAOqJmrx0UzUZdmW2AUXnbQmVqeufXC0HCza9X0CY2AqvXS6nATofDyr1pdCwcuvlpXzZQFoa7wzp5cWPNZ7SZC0co2sVkUlUJ'
            },
            {
                'id': 4,
                'category': cat4,
                'name': 'The St. Jude Hand-Carved Walnut',
                'description': 'Individually sculpted from old-growth Appalachian walnut with bespoke lancet arch colonnade friezes, accented with crushed ivory silk-velvet padding. A master atelier guild masterpiece crafted for heirloom legacy.',
                'material': 'Old-Growth Appalachian Walnut',
                'length': '84″',
                'width': '29″',
                'height': '24″',
                'finish': 'walnut',
                'price': Decimal('4600.00'),
                'stock': 2,
                'fabric': 'velvet',
                'sealing_system': 'Artisan Concealed Bolt Vault Seal',
                'capacity': 'Tested up to 400 lbs',
                'dispatch_type': 'bespoke',
                'provenance_code': 'ETR-AUTH-1102',
                'image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuA-85aPU5xM5vQfRQxt9lTmUUrW-CvK0AbBFhValLKXHFzxPtchayJr_YVejUgystUYZZsS2BJHH-SnE3P5EOYMFcddpz1Cjp8KwaVpOzhBVv4Lu1YBlXTm36q3d0dmaYJfRUXg_SM041_1zcd0adWMF9lp7DHiSEjPB5elkkmKciqOcnmrMgPpmww8i8JVTpzMk48VC5itn77wx_zrrb1EILydctEzVcZW0xSOxazNgwM_HC_7Wlog'
            },
            {
                'id': 5,
                'category': cat2,
                'name': 'The Elysium Brushed Copper',
                'description': 'Naturally rustproof solid 32-ounce pure copper construction featuring hand-burnished warm patina, cast bronze swing handles, and tufted champagne velvet interior. Sealed chamber guarantee with lifetime gasket warranty.',
                'material': 'Solid 32oz Pure Copper',
                'length': '83″',
                'width': '28″',
                'height': '23.5″',
                'finish': 'patina',
                'price': Decimal('5200.00'),
                'stock': 3,
                'fabric': 'velvet',
                'sealing_system': 'Perpetual Sealed Chamber Assurance',
                'capacity': 'Tested up to 500 lbs',
                'dispatch_type': 'ready',
                'provenance_code': 'ETR-AUTH-1205',
                'image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuB_Dv91CRcgXDd2SF18iLsfETbN64VB6NUY8HMyFJCgM1Mna_nzThZZhGs4wZbmEtwadvCwDxAG5UO6KzgiHf-mjBFY6Pb-akZDPHDlGF47TQgPAaK9npgc1-i_hnY60-em3GVdRZMzFdUHuQsk7VMSSOSA-XuTvfYGpmau7YGqnVNsSRd5QNp2Sn4l5xBtVuTH0o_DWnU5ok6iWPlGMK6059_W_qJF64OXf2QKUwfdd-Pb4YthndM2'
            },
            {
                'id': 6,
                'category': cat3,
                'name': 'The Serenity Forest Pine',
                'description': 'Constructed from certified sustainable northern white pine with natural wooden dowel fasteners, warm beeswax rub, and an unbleached organic cotton interior mattress. Zero metal screws, 100% biodegradable return.',
                'material': 'Sustainable Northern White Pine',
                'length': '79″',
                'width': '26.5″',
                'height': '21″',
                'finish': 'beeswax',
                'price': Decimal('1150.00'),
                'stock': 7,
                'fabric': 'cotton',
                'sealing_system': '100% Wooden Joinery',
                'capacity': 'Tested up to 320 lbs',
                'dispatch_type': 'ready',
                'provenance_code': 'ETR-AUTH-1340',
                'image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuDypYFncp9gMYC75_407TVNfMGK-7ltX8cm_GKYIAToG2gLqAULmQg4ikbILVHUSxmEyW8CSMuWgdjs09cJaVp-Bm68ebTGi6_iuNE2jnQZu7dH5xKvhG1a9GPQCpsaHJSabzLL8HW-aVZrbsHdPYhDs78--zhxKM1BQP8cOMjRmouSTpZfiPm9V6fNLcvLEiwjUwtSJRRFme5BGqc_Yv4He24wm3KyvHnrggLiEU_mXLEWX3vzu9sS'
            },
            {
                'id': 7,
                'category': cat1,
                'name': 'The Canterbury Solid Mahogany',
                'description': 'Hand-selected ribbon-grain Honduran mahogany with deep hand-rubbed luster, velvet tufted interior, and solid antiqued brass handles. Reflects traditional English cathedral solemnity and lasting grace.',
                'material': 'Solid Honduran Mahogany',
                'length': '83″',
                'width': '28.5″',
                'height': '23″',
                'finish': 'patina',
                'price': Decimal('3850.00'),
                'stock': 5,
                'fabric': 'velvet',
                'sealing_system': 'Precision Mortise & Tenon Lock',
                'capacity': 'Tested up to 400 lbs',
                'dispatch_type': 'ready',
                'provenance_code': 'ETR-AUTH-1402',
                'image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuCBi8k5J9jpxSrq6_Ig5-qZww3t3WrZ2gCIGvUvgQeVzcjgsS1XkffTjHSYWGNzIWKwY2Id2mX2gtd8sKomhJuINTviUuc7TlVmLKHNgn0cVUrKlL_0duld9XRJrE55Pzec7xwU_U4bDpikodDfMB6HRgInIAjZTxXNjuJ94R6YQPe4xpTux-qXMpbNT-Zpx4vPjsdP3vgnolkGnIWXDdww5xOE_QUHhuD7Hb0rj6tvyyI6wV-3QTu8'
            },
            {
                'id': 8,
                'category': cat2,
                'name': 'The Lincoln Cast Heritage Bronze',
                'description': 'Cast from pure 32-ounce bronze alloy, the noblest of memorial metals. Hand-polished midnight bronze finish with vacuum gasket crypt seal and champagne velvet bed. Fully non-corrosive for eternity.',
                'material': 'Solid Architectural Bronze',
                'length': '83.5″',
                'width': '29″',
                'height': '24″',
                'finish': 'bronze',
                'price': Decimal('5900.00'),
                'stock': 2,
                'fabric': 'velvet',
                'sealing_system': 'Dual Vacuum Crypt Hermetic Gasket',
                'capacity': 'Tested up to 550 lbs',
                'dispatch_type': 'ready',
                'provenance_code': 'ETR-AUTH-1550',
                'image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuDM0IFsljflvXgITtGLWWzZRMPrDRuFEqBelq1-gPiIeX-__OTVsLqT7FVrn1AYQ0rlosEaHHxqEstpxmqWxI1dlHJBOuahDuF9hqB5QfKtI6cx3TM7nPIaJc1jikjz9olp04dMISXJetcmbY9kZKGItu2wlLoseVVYX1icenR6hlIflSDD-kqKgqUaUTO4p4dmtDQdb1TBygCq9_9oMK45DJmxsdhyXiskG5RcJNP6lMoyReQkMOF3'
            },
            {
                'id': 9,
                'category': cat3,
                'name': 'The Eden Woven Bamboo',
                'description': 'Meticulously crafted from fast-growing, renewable organic bamboo canes and rush weaves. Zero nails, formaldehyde-free, with natural calico lining and unbleached cotton pillows.',
                'material': 'Natural Renewable Bamboo',
                'length': '79″',
                'width': '27″',
                'height': '20.5″',
                'finish': 'natural',
                'price': Decimal('1650.00'),
                'stock': 6,
                'fabric': 'cotton',
                'sealing_system': 'Twined Bamboo Fasteners',
                'capacity': 'Tested up to 310 lbs',
                'dispatch_type': 'ready',
                'provenance_code': 'ETR-AUTH-1620',
                'image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuDPdJZjSls9QTrTbI-K6gTgMylPCJFRlY6jEvwD0ieXRoowc-8pW3qn8jMtwlzvBTrdy6cAiHh9xZinl_GcQ9YB-_iom-X3LM3YZCoH4sZuHm0gOUsc2PbBNjDfjjEK5cCxbkwo27EjKLHRk6YSStOAOqJmrx0UzUZdmW2AUXnbQmVqeufXC0HCza9X0CY2AqvXS6nATofDyr1pdCwcuvlpXzZQFoa7wzp5cWPNZ7SZC0co2sVkUlUJ'
            },
            {
                'id': 10,
                'category': cat4,
                'name': 'The Notre Dame Cathedral Relic',
                'description': 'A monument to sacred architecture. Features hand-chiseled pointed gothic arches along the side panels, warm antique walnut wood, hand-gilded bronze corners, and rich ivory silk velvet lining.',
                'material': 'Cathedral Black Walnut & Bronze',
                'length': '85″',
                'width': '30″',
                'height': '24.5″',
                'finish': 'walnut',
                'price': Decimal('6200.00'),
                'stock': 1,
                'fabric': 'velvet',
                'sealing_system': 'Gothic Vault Pin Joinery',
                'capacity': 'Tested up to 450 lbs',
                'dispatch_type': 'bespoke',
                'provenance_code': 'ETR-AUTH-1777',
                'image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuA-85aPU5xM5vQfRQxt9lTmUUrW-CvK0AbBFhValLKXHFzxPtchayJr_YVejUgystUYZZsS2BJHH-SnE3P5EOYMFcddpz1Cjp8KwaVpOzhBVv4Lu1YBlXTm36q3d0dmaYJfRUXg_SM041_1zcd0adWMF9lp7DHiSEjPB5elkkmKciqOcnmrMgPpmww8i8JVTpzMk48VC5itn77wx_zrrb1EILydctEzVcZW0xSOxazNgwM_HC_7Wlog'
            },
            {
                'id': 11,
                'category': cat2,
                'name': 'The Valhalla 18G Nocturne Steel',
                'description': 'Constructed from cold-rolled 18-gauge protective steel, electrostatically treated with midnight bronze powder coat and hermetic dual neoprene gaskets. Quiet dignity and high endurance.',
                'material': '18-Gauge Cold-Rolled Steel',
                'length': '83″',
                'width': '28″',
                'height': '23″',
                'finish': 'bronze',
                'price': Decimal('2950.00'),
                'stock': 5,
                'fabric': 'crepe',
                'sealing_system': 'Dual Neoprene Gasket Hermetic Lock',
                'capacity': 'Tested up to 420 lbs',
                'dispatch_type': 'ready',
                'provenance_code': 'ETR-AUTH-1880',
                'image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuB_Dv91CRcgXDd2SF18iLsfETbN64VB6NUY8HMyFJCgM1Mna_nzThZZhGs4wZbmEtwadvCwDxAG5UO6KzgiHf-mjBFY6Pb-akZDPHDlGF47TQgPAaK9npgc1-i_hnY60-em3GVdRZMzFdUHuQsk7VMSSOSA-XuTvfYGpmau7YGqnVNsSRd5QNp2Sn4l5xBtVuTH0o_DWnU5ok6iWPlGMK6059_W_qJF64OXf2QKUwfdd-Pb4YthndM2'
            },
            {
                'id': 12,
                'category': cat1,
                'name': 'The Glastonbury Alabaster Ash',
                'description': 'Milled from high-purity northern white ash with warm honey stain and subtle satin wax sheen. Lined with hand-tailored pearl crepe interior and reinforced solid brass swing bar handles.',
                'material': 'Northern White Ash',
                'length': '82″',
                'width': '27.5″',
                'height': '22.5″',
                'finish': 'satin',
                'price': Decimal('2600.00'),
                'stock': 4,
                'fabric': 'crepe',
                'sealing_system': 'Precision Hand-Fitted Dowel Seal',
                'capacity': 'Tested up to 360 lbs',
                'dispatch_type': 'ready',
                'provenance_code': 'ETR-AUTH-1994',
                'image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuDypYFncp9gMYC75_407TVNfMGK-7ltX8cm_GKYIAToG2gLqAULmQg4ikbILVHUSxmEyW8CSMuWgdjs09cJaVp-Bm68ebTGi6_iuNE2jnQZu7dH5xKvhG1a9GPQCpsaHJSabzLL8HW-aVZrbsHdPYhDs78--zhxKM1BQP8cOMjRmouSTpZfiPm9V6fNLcvLEiwjUwtSJRRFme5BGqc_Yv4He24wm3KyvHnrggLiEU_mXLEWX3vzu9sS'
            }
        ]

        for p_data in products_data:
            img_url = p_data.pop('image')
            prov_code = p_data['provenance_code']
            prod, _ = Product.objects.update_or_create(id=p_data['id'], defaults=p_data)
            ProductImage.objects.get_or_create(product=prod, image_url=img_url)
            AuthenticityCertificate.objects.get_or_create(
                product=prod,
                defaults={
                    'verification_code': prov_code,
                    'qr_code_url': f'https://api.qrserver.com/v1/create-qr-code/?size=160x160&data={prov_code}',
                    'issued_by': admin,
                    'is_active': True
                }
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(products_data)} memorial products and certificates.'))

        # 5. Sample Order & Invoice
        if not Order.objects.filter(user=buyer).exists():
            order = Order.objects.create(
                user=buyer,
                shipping_address=address,
                status='confirmed',
                total_amount=Decimal('2850.00'),
                mortuary_name='Graceview Memorial Sanctuary',
                mortuary_director='Director Robert Sterling',
                mortuary_phone='+1 (555) 890-1234',
                delivery_notes='Deliver directly to loading bay B by Thursday morning for Friday service.'
            )
            p1 = Product.objects.get(id=1)
            OrderItem.objects.create(order=order, product=p1, quantity=1, unit_price=Decimal('2850.00'))
            Payment.objects.create(order=order, method='Sandbox Card', transaction_ref='TXN-ETR-849204', status='success')
            Invoice.objects.create(order=order, invoice_number='INV-2026-0042', total_amount=Decimal('2850.00'), status='PAID')
            self.stdout.write(self.style.SUCCESS('Sample order, payment, and invoice created.'))

        # 6. Sample Enquiry
        if not Enquiry.objects.filter(user=buyer).exists():
            Enquiry.objects.create(
                user=buyer,
                name='Eleanor Vance',
                email='eleanor@example.com',
                phone='+1 (555) 234-5678',
                mortuary_location='Oakridge Mortuary, Portland OR',
                urgency_level='<24h',
                custom_type='Custom Monogram Carving',
                message='We require expedited dispatch of The Westminster Oak with monogrammed initials "H.V." on the head end panel for a Saturday memorial service.',
                admin_response='Bereavement Counselor Marcus has confirmed expedited hand-carving in our workshop. Scheduled for mortuary direct courier transfer within 18 hours.',
                status='Responded'
            )
            self.stdout.write(self.style.SUCCESS('Sample enquiry created.'))

        # 7. System Settings
        SystemSetting.objects.get_or_create(
            setting_key='bereavement_hotline',
            defaults={'setting_value': '1-800-ETERNUM (383-7686)', 'updated_by': admin}
        )
        SystemSetting.objects.get_or_create(
            setting_key='dispatch_email',
            defaults={'setting_value': 'counselor@eternum-memorial.com', 'updated_by': admin}
        )
        SystemSetting.objects.get_or_create(
            setting_key='ftc_compliance_notice',
            defaults={'setting_value': 'Under FTC 16 CFR Part 453, mortuaries cannot reject or penalize third-party casket deliveries.', 'updated_by': admin}
        )

        self.stdout.write(self.style.SUCCESS('Eternum database seeding completed successfully!'))
