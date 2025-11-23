"""
Management command to load test data for Skinova Clinic
Run with: python manage.py load_test_data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, time, timedelta
from decimal import Decimal

from core.models import Client, User
from appointments.models import Service, StaffMember, Appointment, Package, ClientPackage, ClientServiceSession
from pos.models import Product, Order, OrderItem


class Command(BaseCommand):
    help = 'Loads test data for Skinova Clinic'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            Appointment.objects.all().delete()
            OrderItem.objects.all().delete()
            Order.objects.all().delete()
            Product.objects.all().delete()
            ClientPackage.objects.all().delete()
            ClientServiceSession.objects.all().delete()
            Package.objects.all().delete()
            Service.objects.all().delete()
            StaffMember.objects.all().delete()
            Client.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('Data cleared!'))

        self.stdout.write(self.style.SUCCESS('Loading test data...'))

        # Create Services
        services_data = [
            {
                'name': 'Classic Facial',
                'description': 'Deep cleansing facial with extraction and moisturizing',
                'duration': 60,
                'price': Decimal('85.00'),
            },
            {
                'name': 'Hydrating Facial',
                'description': 'Intense hydration treatment for dry skin',
                'duration': 75,
                'price': Decimal('120.00'),
            },
            {
                'name': 'Anti-Aging Facial',
                'description': 'Rejuvenating treatment with anti-aging serums',
                'duration': 90,
                'price': Decimal('150.00'),
            },
            {
                'name': 'Acne Treatment',
                'description': 'Specialized treatment for acne-prone skin',
                'duration': 60,
                'price': Decimal('95.00'),
            },
            {
                'name': 'Microdermabrasion',
                'description': 'Deep exfoliation treatment',
                'duration': 45,
                'price': Decimal('110.00'),
            },
            {
                'name': 'Chemical Peel',
                'description': 'Professional chemical peel treatment',
                'duration': 60,
                'price': Decimal('130.00'),
            },
            {
                'name': 'LED Light Therapy',
                'description': 'LED light treatment for skin rejuvenation',
                'duration': 30,
                'price': Decimal('75.00'),
            },
            {
                'name': 'Botox Consultation',
                'description': 'Consultation for Botox treatment',
                'duration': 30,
                'price': Decimal('50.00'),
            },
            {
                'name': 'Laser Hair Removal',
                'description': 'Professional laser hair removal treatment',
                'duration': 45,
                'price': Decimal('150.00'),
                'sessions_required': 6,  # Multi-session service
            },
            {
                'name': 'PRP Treatment',
                'description': 'Platelet-Rich Plasma facial rejuvenation',
                'duration': 60,
                'price': Decimal('200.00'),
                'sessions_required': 3,  # Multi-session service
            },
            {
                'name': 'RF Skin Tightening',
                'description': 'Radio Frequency skin tightening treatment',
                'duration': 60,
                'price': Decimal('180.00'),
                'sessions_required': 4,  # Multi-session service
            },
            {
                'name': 'Microneedling',
                'description': 'Collagen induction therapy',
                'duration': 45,
                'price': Decimal('120.00'),
                'sessions_required': 3,  # Multi-session service
            },
        ]

        services = []
        for service_data in services_data:
            # Ensure sessions_required defaults to 1 if not provided
            if 'sessions_required' not in service_data:
                service_data['sessions_required'] = 1
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )
            # Update sessions_required if service already exists
            if not created and service.sessions_required != service_data.get('sessions_required', 1):
                service.sessions_required = service_data.get('sessions_required', 1)
                service.save()
            services.append(service)
            if created:
                self.stdout.write(f'  Created service: {service.name}')

        # Create Staff Members
        staff_data = [
            {
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'email': 'sarah.johnson@skinova.com',
                'phone_number': '+961 03 441 339',
                'specialization': 'Lead Esthetician',
                'bio': '10 years of experience in skincare treatments',
                'monday_start': time(9, 0),
                'monday_end': time(17, 0),
                'tuesday_start': time(9, 0),
                'tuesday_end': time(17, 0),
                'wednesday_start': time(9, 0),
                'wednesday_end': time(17, 0),
                'thursday_start': time(9, 0),
                'thursday_end': time(17, 0),
                'friday_start': time(9, 0),
                'friday_end': time(15, 0),
            },
            {
                'first_name': 'Emily',
                'last_name': 'Chen',
                'email': 'emily.chen@skinova.com',
                'phone_number': '+961 03 441 339',
                'specialization': 'Facial Specialist',
                'bio': 'Specialized in anti-aging and hydrating treatments',
                'monday_start': time(10, 0),
                'monday_end': time(18, 0),
                'tuesday_start': time(10, 0),
                'tuesday_end': time(18, 0),
                'wednesday_start': time(10, 0),
                'wednesday_end': time(18, 0),
                'thursday_start': time(10, 0),
                'thursday_end': time(18, 0),
                'friday_start': time(10, 0),
                'friday_end': time(16, 0),
            },
            {
                'first_name': 'Dr. Michael',
                'last_name': 'Rodriguez',
                'email': 'michael.rodriguez@skinova.com',
                'phone_number': '+961 03 441 339',
                'specialization': 'Dermatologist',
                'bio': 'Board-certified dermatologist specializing in cosmetic procedures',
                'monday_start': time(8, 0),
                'monday_end': time(16, 0),
                'tuesday_start': time(8, 0),
                'tuesday_end': time(16, 0),
                'wednesday_start': None,
                'wednesday_end': None,
                'thursday_start': time(8, 0),
                'thursday_end': time(16, 0),
                'friday_start': time(8, 0),
                'friday_end': time(14, 0),
            },
        ]

        staff_members = []
        for staff_info in staff_data:
            staff, created = StaffMember.objects.get_or_create(
                email=staff_info['email'],
                defaults=staff_info
            )
            staff_members.append(staff)
            if created:
                self.stdout.write(f'  Created staff: {staff.get_full_name()}')

        # Create Clients
        clients_data = [
            {
                'first_name': 'Amanda',
                'last_name': 'Smith',
                'email': 'amanda.smith@email.com',
                'phone_number': '+961 03 441 339',
                'date_of_birth': date(1990, 5, 15),
                'address': '123 Main Street, Beirut, Lebanon',
                'notes': 'Prefers morning appointments, sensitive skin',
            },
            {
                'first_name': 'Jessica',
                'last_name': 'Williams',
                'email': 'jessica.williams@email.com',
                'phone_number': '+961 03 441 339',
                'date_of_birth': date(1985, 8, 22),
                'address': '456 Oak Avenue, Beirut, Lebanon',
                'notes': 'Regular client, loves hydrating facials',
            },
            {
                'first_name': 'Maria',
                'last_name': 'Garcia',
                'email': 'maria.garcia@email.com',
                'phone_number': '+961 03 441 339',
                'date_of_birth': date(1992, 3, 10),
                'address': '789 Pine Road, Beirut, Lebanon',
                'notes': 'New client, interested in anti-aging treatments',
            },
            {
                'first_name': 'Jennifer',
                'last_name': 'Brown',
                'email': 'jennifer.brown@email.com',
                'phone_number': '+961 03 441 339',
                'date_of_birth': date(1988, 11, 30),
                'address': '321 Elm Street, Beirut, Lebanon',
                'notes': 'Has acne concerns, prefers Dr. Rodriguez',
            },
            {
                'first_name': 'Lisa',
                'last_name': 'Anderson',
                'email': 'lisa.anderson@email.com',
                'phone_number': '+961 03 441 339',
                'date_of_birth': date(1995, 7, 5),
                'address': '654 Maple Drive, Beirut, Lebanon',
                'notes': 'Regular facial treatments monthly',
            },
            {
                'first_name': 'Sophia',
                'last_name': 'Martinez',
                'email': 'sophia.martinez@email.com',
                'phone_number': '+961 03 441 339',
                'date_of_birth': date(1987, 2, 18),
                'address': '987 Cedar Lane, Beirut, Lebanon',
                'notes': 'VIP client, prefers afternoon appointments',
            },
        ]

        clients = []
        for client_data in clients_data:
            client, created = Client.objects.get_or_create(
                email=client_data['email'],
                defaults=client_data
            )
            clients.append(client)
            if created:
                self.stdout.write(f'  Created client: {client.get_full_name()}')

        # Create Products
        products_data = [
            {
                'name': 'Hydrating Serum',
                'description': 'Intensive hydrating serum with hyaluronic acid',
                'sku': 'SKU-HS-001',
                'price': Decimal('45.00'),
                'stock_qty': 25,
            },
            {
                'name': 'Vitamin C Brightening Cream',
                'description': 'Brightening cream with Vitamin C and antioxidants',
                'sku': 'SKU-VC-002',
                'price': Decimal('65.00'),
                'stock_qty': 18,
            },
            {
                'name': 'Gentle Cleanser',
                'description': 'Daily gentle cleanser for all skin types',
                'sku': 'SKU-GC-003',
                'price': Decimal('28.00'),
                'stock_qty': 35,
            },
            {
                'name': 'SPF 50 Sunscreen',
                'description': 'Broad spectrum sunscreen for daily protection',
                'sku': 'SKU-SPF-004',
                'price': Decimal('42.00'),
                'stock_qty': 42,
            },
            {
                'name': 'Retinol Night Cream',
                'description': 'Anti-aging night cream with retinol',
                'sku': 'SKU-RNC-005',
                'price': Decimal('85.00'),
                'stock_qty': 12,
            },
            {
                'name': 'Acne Spot Treatment',
                'description': 'Targeted treatment for acne spots',
                'sku': 'SKU-AST-006',
                'price': Decimal('32.00'),
                'stock_qty': 28,
            },
            {
                'name': 'Exfoliating Toner',
                'description': 'Gentle exfoliating toner with AHA/BHA',
                'sku': 'SKU-ET-007',
                'price': Decimal('38.00'),
                'stock_qty': 20,
            },
            {
                'name': 'Eye Cream',
                'description': 'Firming and hydrating eye cream',
                'sku': 'SKU-EC-008',
                'price': Decimal('55.00'),
                'stock_qty': 15,
            },
            {
                'name': 'Face Mask Set',
                'description': 'Set of 5 hydrating face masks',
                'sku': 'SKU-FMS-009',
                'price': Decimal('48.00'),
                'stock_qty': 30,
            },
            {
                'name': 'Anti-Aging Serum',
                'description': 'Advanced anti-aging serum with peptides',
                'sku': 'SKU-AAS-010',
                'price': Decimal('95.00'),
                'stock_qty': 8,  # Low stock for testing
            },
        ]

        products = []
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                sku=product_data['sku'],
                defaults=product_data
            )
            products.append(product)
            if created:
                self.stdout.write(f'  Created product: {product.name}')

        # Create Appointments
        today = timezone.now().date()
        appointments_data = [
            {
                'client': clients[0],
                'service': services[0],  # Classic Facial
                'staff': staff_members[0],  # Sarah Johnson
                'appointment_date': today + timedelta(days=2),
                'appointment_time': time(10, 0),
                'status': 'confirmed',
                'notes': 'First time client, excited about the treatment',
            },
            {
                'client': clients[1],
                'service': services[1],  # Hydrating Facial
                'staff': staff_members[1],  # Emily Chen
                'appointment_date': today + timedelta(days=3),
                'appointment_time': time(14, 0),
                'status': 'confirmed',
                'notes': 'Regular monthly appointment',
            },
            {
                'client': clients[2],
                'service': services[2],  # Anti-Aging Facial
                'staff': staff_members[1],  # Emily Chen
                'appointment_date': today + timedelta(days=5),
                'appointment_time': time(11, 0),
                'status': 'pending',
                'notes': 'New to anti-aging treatments',
            },
            {
                'client': clients[3],
                'service': services[3],  # Acne Treatment
                'staff': staff_members[2],  # Dr. Michael Rodriguez
                'appointment_date': today + timedelta(days=1),
                'appointment_time': time(9, 0),
                'status': 'confirmed',
                'notes': 'Follow-up appointment',
            },
            {
                'client': clients[4],
                'service': services[0],  # Classic Facial
                'staff': staff_members[0],  # Sarah Johnson
                'appointment_date': today - timedelta(days=5),
                'appointment_time': time(13, 0),
                'status': 'completed',
                'notes': 'Treatment went well, client was satisfied',
            },
            {
                'client': clients[5],
                'service': services[4],  # Microdermabrasion
                'staff': staff_members[0],  # Sarah Johnson
                'appointment_date': today - timedelta(days=3),
                'appointment_time': time(15, 0),
                'status': 'completed',
                'notes': 'Excellent results, scheduled follow-up',
            },
        ]

        for apt_data in appointments_data:
            try:
                appointment, created = Appointment.objects.get_or_create(
                    client=apt_data['client'],
                    service=apt_data['service'],
                    staff=apt_data['staff'],
                    appointment_date=apt_data['appointment_date'],
                    appointment_time=apt_data['appointment_time'],
                    defaults={
                        'status': apt_data['status'],
                        'notes': apt_data['notes'],
                    }
                )
                if created:
                    self.stdout.write(f'  Created appointment: {appointment}')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  Could not create appointment: {e}'))

        # Create Orders
        orders_data = [
            {
                'client': clients[4],  # Lisa Anderson
                'total_price': Decimal('113.00'),
                'payment_method': 'card',
                'payment_status': 'paid',
                'notes': 'Order from completed appointment',
            },
            {
                'client': clients[5],  # Sophia Martinez
                'total_price': Decimal('158.00'),
                'payment_method': 'cash',
                'payment_status': 'paid',
                'notes': 'Walk-in purchase',
            },
            {
                'client': None,  # Walk-in
                'total_price': Decimal('70.00'),
                'payment_method': 'cash',
                'payment_status': 'paid',
                'notes': 'Walk-in customer, no client record',
            },
            {
                'client': clients[0],  # Amanda Smith
                'total_price': Decimal('140.00'),
                'payment_method': 'card',
                'payment_status': 'paid',
                'notes': 'Pre-appointment purchase',
            },
        ]

        orders = []
        for order_data in orders_data:
            order = Order.objects.create(**order_data)
            orders.append(order)
            self.stdout.write(f'  Created order: Order #{order.id}')

        # Create Order Items
        # Order 1: Lisa Anderson - products from completed appointment
        OrderItem.objects.create(
            order=orders[0],
            product=products[0],  # Hydrating Serum
            quantity=1,
            unit_price=products[0].price,
            subtotal=products[0].price,
        )
        OrderItem.objects.create(
            order=orders[0],
            product=products[3],  # SPF 50 Sunscreen
            quantity=1,
            unit_price=products[3].price,
            subtotal=products[3].price,
        )
        OrderItem.objects.create(
            order=orders[0],
            service=services[0],  # Classic Facial
            quantity=1,
            unit_price=services[0].price,
            subtotal=services[0].price,
            appointment=Appointment.objects.filter(
                client=clients[4],
                status='completed'
            ).first(),
        )

        # Order 2: Sophia Martinez - products and service
        OrderItem.objects.create(
            order=orders[1],
            product=products[1],  # Vitamin C Brightening Cream
            quantity=1,
            unit_price=products[1].price,
            subtotal=products[1].price,
        )
        OrderItem.objects.create(
            order=orders[1],
            product=products[7],  # Eye Cream
            quantity=1,
            unit_price=products[7].price,
            subtotal=products[7].price,
        )
        OrderItem.objects.create(
            order=orders[1],
            service=services[4],  # Microdermabrasion
            quantity=1,
            unit_price=services[4].price,
            subtotal=services[4].price,
            appointment=Appointment.objects.filter(
                client=clients[5],
                status='completed'
            ).first(),
        )

        # Order 3: Walk-in - just products
        OrderItem.objects.create(
            order=orders[2],
            product=products[2],  # Gentle Cleanser
            quantity=1,
            unit_price=products[2].price,
            subtotal=products[2].price,
        )
        OrderItem.objects.create(
            order=orders[2],
            product=products[8],  # Face Mask Set
            quantity=1,
            unit_price=products[8].price,
            subtotal=products[8].price,
        )

        # Order 4: Amanda Smith - products
        OrderItem.objects.create(
            order=orders[3],
            product=products[4],  # Retinol Night Cream
            quantity=1,
            unit_price=products[4].price,
            subtotal=products[4].price,
        )
        OrderItem.objects.create(
            order=orders[3],
            product=products[6],  # Exfoliating Toner
            quantity=1,
            unit_price=products[6].price,
            subtotal=products[6].price,
        )

        # Create Packages
        packages_data = [
            {
                'name': 'Premium Facial Package',
                'description': 'Complete facial treatment package with multiple services',
                'total_sessions': 10,
                'price': Decimal('850.00'),
                'services': [services[0], services[1], services[2], services[4]],  # Classic, Hydrating, Anti-Aging, Microdermabrasion
            },
            {
                'name': 'Acne Clear Package',
                'description': 'Comprehensive acne treatment package',
                'total_sessions': 8,
                'price': Decimal('680.00'),
                'services': [services[3], services[6], services[4]],  # Acne Treatment, LED Therapy, Microdermabrasion
            },
            {
                'name': 'Rejuvenation Complete',
                'description': 'Full skin rejuvenation package',
                'total_sessions': 12,
                'price': Decimal('1200.00'),
                'services': [services[1], services[2], services[5], services[6], services[4]],  # Hydrating, Anti-Aging, Chemical Peel, LED, Microdermabrasion
            },
            {
                'name': 'Quick Glow Package',
                'description': 'Quick treatment package for busy clients',
                'total_sessions': 6,
                'price': Decimal('480.00'),
                'services': [services[0], services[4], services[6]],  # Classic Facial, Microdermabrasion, LED Therapy
            },
        ]

        packages = []
        for package_data in packages_data:
            services_list = package_data.pop('services')
            package, created = Package.objects.get_or_create(
                name=package_data['name'],
                defaults=package_data
            )
            # Set services
            package.services.set(services_list)
            packages.append(package)
            if created:
                self.stdout.write(f'  Created package: {package.name} with {len(services_list)} services')

        # Assign Packages to Clients (ClientPackage)
        client_packages_data = [
            {
                'client': clients[0],  # Amanda Smith
                'package': packages[0],  # Premium Facial Package
                'sessions_completed': 3,
                'is_completed': False,
            },
            {
                'client': clients[1],  # Jessica Williams
                'package': packages[1],  # Acne Clear Package
                'sessions_completed': 5,
                'is_completed': False,
            },
            {
                'client': clients[2],  # Maria Garcia
                'package': packages[2],  # Rejuvenation Complete
                'sessions_completed': 2,
                'is_completed': False,
            },
            {
                'client': clients[4],  # Lisa Anderson
                'package': packages[3],  # Quick Glow Package
                'sessions_completed': 6,  # Completed!
                'is_completed': True,
            },
            {
                'client': clients[5],  # Sophia Martinez
                'package': packages[0],  # Premium Facial Package
                'sessions_completed': 8,
                'is_completed': False,
            },
        ]

        client_packages = []
        for cp_data in client_packages_data:
            cp, created = ClientPackage.objects.get_or_create(
                client=cp_data['client'],
                package=cp_data['package'],
                defaults={
                    'sessions_completed': cp_data['sessions_completed'],
                    'is_completed': cp_data['is_completed'],
                }
            )
            client_packages.append(cp)
            if created:
                self.stdout.write(f'  Assigned package "{cp.package.name}" to {cp.client.get_full_name()} ({cp.sessions_completed}/{cp.package.total_sessions} sessions)')

        # Create Service Sessions (for multi-session services)
        service_sessions_data = [
            {
                'client': clients[0],  # Amanda Smith
                'service': services[8],  # Laser Hair Removal (6 sessions)
                'sessions_completed': 2,
                'is_completed': False,
            },
            {
                'client': clients[1],  # Jessica Williams
                'service': services[9],  # PRP Treatment (3 sessions)
                'sessions_completed': 1,
                'is_completed': False,
            },
            {
                'client': clients[2],  # Maria Garcia
                'service': services[10],  # RF Skin Tightening (4 sessions)
                'sessions_completed': 3,
                'is_completed': False,
            },
            {
                'client': clients[3],  # Jennifer Brown
                'service': services[11],  # Microneedling (3 sessions)
                'sessions_completed': 3,  # Completed!
                'is_completed': True,
            },
            {
                'client': clients[5],  # Sophia Martinez
                'service': services[8],  # Laser Hair Removal (6 sessions)
                'sessions_completed': 4,
                'is_completed': False,
            },
            {
                'client': clients[0],  # Amanda Smith
                'service': services[9],  # PRP Treatment (3 sessions)
                'sessions_completed': 2,
                'is_completed': False,
            },
        ]

        service_sessions = []
        for ss_data in service_sessions_data:
            ss, created = ClientServiceSession.objects.get_or_create(
                client=ss_data['client'],
                service=ss_data['service'],
                defaults={
                    'sessions_completed': ss_data['sessions_completed'],
                    'is_completed': ss_data['is_completed'],
                }
            )
            service_sessions.append(ss)
            if created:
                self.stdout.write(f'  Started tracking "{ss.service.name}" for {ss.client.get_full_name()} ({ss.sessions_completed}/{ss.service.sessions_required} sessions)')

        self.stdout.write(self.style.SUCCESS('\n✓ Test data loaded successfully!'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(services)} Services'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(staff_members)} Staff Members'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(clients)} Clients'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(products)} Products'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(packages)} Packages'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(client_packages)} Client Package Assignments'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(service_sessions)} Service Session Trackings'))
        self.stdout.write(self.style.SUCCESS(f'  - {Appointment.objects.count()} Appointments'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(orders)} Orders'))
        self.stdout.write(self.style.SUCCESS(f'  - {OrderItem.objects.count()} Order Items'))

