from django.test import TestCase, Client as TestClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.messages import get_messages
from .models import Client
from appointments.models import Package, ClientPackage, Service, ClientServiceSession
from pathlib import Path
from django.conf import settings
import os

User = get_user_model()


class ClientProfileViewTests(TestCase):
    """Test client profile page and related actions"""
    
    def setUp(self):
        """Set up test data"""
        self.client_obj = Client.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone_number="1234567890"
        )
        
        self.user = User.objects.create_user(
            username='admin',
            password='testpass123',
            is_superuser=True,
            is_staff=True
        )
        
        self.service = Service.objects.create(
            name="Facial Treatment",
            duration=60,
            price=100.00,
            sessions_required=3,
            is_active=True
        )
        
        self.package = Package.objects.create(
            name="Premium Package",
            total_sessions=6,
            price=500.00,
            is_active=True
        )
        self.package.services.add(self.service)
        
        self.client = TestClient()
    
    def test_client_profile_page_loads(self):
        """Test that client profile page loads successfully"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('client_profile', args=[self.client_obj.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")
        self.assertContains(response, "Treatment Packages")
    
    def test_assign_package_to_client(self):
        """Test assigning a package to a client"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.post(
            reverse('assign_package_to_client', args=[self.client_obj.id]),
            {'package_id': self.package.id},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ClientPackage.objects.filter(
            client=self.client_obj,
            package=self.package
        ).exists())
        
        # Check for success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('assigned successfully' in str(m) for m in messages))
    
    def test_assign_package_without_selection(self):
        """Test assigning package without selecting one"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.post(
            reverse('assign_package_to_client', args=[self.client_obj.id]),
            {},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Please select a package' in str(m) for m in messages))
    
    def test_assign_duplicate_package(self):
        """Test assigning the same package twice"""
        self.client.login(username='admin', password='testpass123')
        # Assign first time
        ClientPackage.objects.create(
            client=self.client_obj,
            package=self.package,
            sessions_completed=0,
            is_completed=False
        )
        
        # Try to assign again
        response = self.client.post(
            reverse('assign_package_to_client', args=[self.client_obj.id]),
            {'package_id': self.package.id},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('already assigned' in str(m) for m in messages))
    
    def test_add_package_session(self):
        """Test adding a session to a client package"""
        self.client.login(username='admin', password='testpass123')
        client_package = ClientPackage.objects.create(
            client=self.client_obj,
            package=self.package,
            sessions_completed=0,
            is_completed=False
        )
        
        response = self.client.post(
            reverse('add_package_session', args=[client_package.id]),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        client_package.refresh_from_db()
        self.assertEqual(client_package.sessions_completed, 1)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Session added' in str(m) for m in messages))
    
    def test_add_session_to_completed_package(self):
        """Test adding session to already completed package"""
        self.client.login(username='admin', password='testpass123')
        client_package = ClientPackage.objects.create(
            client=self.client_obj,
            package=self.package,
            sessions_completed=self.package.total_sessions,
            is_completed=True
        )
        
        response = self.client.post(
            reverse('add_package_session', args=[client_package.id]),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('already completed' in str(m) for m in messages))
    
    def test_add_service_session(self):
        """Test adding a session to a service"""
        self.client.login(username='admin', password='testpass123')
        service_session = ClientServiceSession.objects.create(
            client=self.client_obj,
            service=self.service,
            sessions_completed=0,
            is_completed=False
        )
        
        response = self.client.post(
            reverse('add_service_session', args=[service_session.id]),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        service_session.refresh_from_db()
        self.assertEqual(service_session.sessions_completed, 1)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Session added' in str(m) for m in messages))
    
    def test_client_profile_requires_login(self):
        """Test that client profile requires authentication"""
        response = self.client.get(reverse('client_profile', args=[self.client_obj.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login


class BackupManagementTests(TestCase):
    """Test backup management functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='admin',
            password='testpass123',
            is_superuser=True,
            is_staff=True
        )
        self.client = TestClient()
    
    def test_backup_management_page_loads(self):
        """Test that backup management page loads"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('backup_management'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Backup Management")
    
    def test_backup_management_requires_superuser(self):
        """Test that non-superusers cannot access backup management"""
        regular_user = User.objects.create_user(
            username='regular',
            password='testpass123',
            is_superuser=False,
            is_staff=True
        )
        self.client.login(username='regular', password='testpass123')
        response = self.client.get(reverse('backup_management'))
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_create_backup(self):
        """Test creating a backup"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.post(
            reverse('create_backup'),
            follow=True
        )
        # Should redirect back to backup management
        self.assertEqual(response.status_code, 200)
    
    def test_download_backup_requires_superuser(self):
        """Test that download backup requires superuser"""
        regular_user = User.objects.create_user(
            username='regular',
            password='testpass123',
            is_superuser=False,
            is_staff=True
        )
        self.client.login(username='regular', password='testpass123')
        response = self.client.get(reverse('download_backup', args=['test.zip']))
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_delete_backup_requires_superuser(self):
        """Test that delete backup requires superuser"""
        regular_user = User.objects.create_user(
            username='regular',
            password='testpass123',
            is_superuser=False,
            is_staff=True
        )
        self.client.login(username='regular', password='testpass123')
        response = self.client.post(reverse('delete_backup', args=['test.zip']))
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_download_nonexistent_backup(self):
        """Test downloading a backup that doesn't exist"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(
            reverse('download_backup', args=['nonexistent.zip']),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('not found' in str(m) for m in messages))
    
    def test_delete_nonexistent_backup(self):
        """Test deleting a backup that doesn't exist"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.post(
            reverse('delete_backup', args=['nonexistent.zip']),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('not found' in str(m) for m in messages))
