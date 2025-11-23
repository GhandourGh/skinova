from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User Model for Admin login only.
    Only Admin accounts exist in the system.
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='admin',
        help_text="User's role in the system"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_admin_user(self):
        """Check if user is admin"""
        return self.role == 'admin' or self.is_superuser
    
    def save(self, *args, **kwargs):
        # Admin users need is_staff=True to access admin
        if self.role == 'admin' or self.is_superuser:
            self.is_staff = True
        super().save(*args, **kwargs)


class Client(models.Model):
    """
    Client model - separate from User authentication.
    Clients don't have passwords, just information records.
    """
    first_name = models.CharField(
        max_length=100,
        help_text="First name"
    )
    last_name = models.CharField(
        max_length=100,
        help_text="Last name"
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Contact phone number"
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        help_text="Date of birth"
    )
    address = models.TextField(
        blank=True,
        null=True,
        help_text="Address"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional client notes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
