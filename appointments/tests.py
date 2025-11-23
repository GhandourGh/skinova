from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import Client
from .models import Service, Package, ClientPackage, ClientServiceSession, StaffMember, Appointment
from django.utils import timezone
from datetime import date, time

User = get_user_model()


class AppointmentModelTests(TestCase):
    """Test appointment model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client_obj = Client.objects.create(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com"
        )
        
        self.service = Service.objects.create(
            name="Facial",
            duration=60,
            price=100.00,
            sessions_required=1
        )
        
        self.staff = StaffMember.objects.create(
            first_name="Dr.",
            last_name="Johnson",
            is_active=True
        )
    
    def test_appointment_creation(self):
        """Test creating an appointment"""
        appointment = Appointment.objects.create(
            client=self.client_obj,
            service=self.service,
            staff=self.staff,
            appointment_date=date.today(),
            appointment_time=time(10, 0),
            status='pending'
        )
        self.assertIsNotNone(appointment)
        self.assertEqual(appointment.status, 'pending')
    
    def test_appointment_str_representation(self):
        """Test appointment string representation"""
        appointment = Appointment.objects.create(
            client=self.client_obj,
            service=self.service,
            staff=self.staff,
            appointment_date=date.today(),
            appointment_time=time(10, 0)
        )
        self.assertIn("Jane Smith", str(appointment))
        self.assertIn("Facial", str(appointment))
    
    def test_appointment_end_time_calculation(self):
        """Test appointment end time calculation"""
        appointment = Appointment.objects.create(
            client=self.client_obj,
            service=self.service,
            staff=self.staff,
            appointment_date=date.today(),
            appointment_time=time(10, 0)
        )
        end_time = appointment.get_end_time()
        # Service duration is 60 minutes, so end time should be 11:00
        self.assertEqual(end_time.hour, 11)
        self.assertEqual(end_time.minute, 0)


class PackageModelTests(TestCase):
    """Test package model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.service1 = Service.objects.create(
            name="Service 1",
            duration=30,
            price=50.00
        )
        self.service2 = Service.objects.create(
            name="Service 2",
            duration=45,
            price=75.00
        )
        self.service3 = Service.objects.create(
            name="Service 3",
            duration=60,
            price=100.00
        )
    
    def test_package_creation(self):
        """Test creating a package"""
        package = Package.objects.create(
            name="Test Package",
            total_sessions=6,
            price=500.00
        )
        package.services.add(self.service1, self.service2, self.service3)
        self.assertIsNotNone(package)
        self.assertEqual(package.services.count(), 3)
    
    def test_package_discount_calculation(self):
        """Test package discount calculation"""
        package = Package.objects.create(
            name="Discounted Package",
            total_sessions=6,
            original_price=600.00,
            price=500.00
        )
        self.assertTrue(package.has_discount())
        self.assertEqual(package.get_discount_percentage(), 17)  # ~17% discount
    
    def test_client_package_progress(self):
        """Test client package progress tracking"""
        client = Client.objects.create(
            first_name="Test",
            last_name="Client"
        )
        package = Package.objects.create(
            name="Test Package",
            total_sessions=6,
            price=500.00
        )
        
        client_package = ClientPackage.objects.create(
            client=client,
            package=package,
            sessions_completed=3
        )
        
        self.assertEqual(client_package.get_progress_percentage(), 50)
        self.assertEqual(client_package.get_remaining_sessions(), 3)
    
    def test_client_package_add_session(self):
        """Test adding a session to client package"""
        client = Client.objects.create(
            first_name="Test",
            last_name="Client"
        )
        package = Package.objects.create(
            name="Test Package",
            total_sessions=3,
            price=500.00
        )
        
        client_package = ClientPackage.objects.create(
            client=client,
            package=package,
            sessions_completed=0
        )
        
        # Add sessions
        self.assertTrue(client_package.add_session())
        client_package.refresh_from_db()
        self.assertEqual(client_package.sessions_completed, 1)
        self.assertFalse(client_package.is_completed)
        
        # Complete the package
        client_package.add_session()
        client_package.add_session()
        client_package.refresh_from_db()
        self.assertTrue(client_package.is_completed)
        self.assertIsNotNone(client_package.completed_date)
