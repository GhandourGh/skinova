from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.models import Client


class Service(models.Model):
    """
    Services offered by the clinic (e.g., Facial, Botox, etc.)
    """
    name = models.CharField(
        max_length=200,
        help_text="Service name"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Service description"
    )
    duration = models.PositiveIntegerField(
        help_text="Duration in minutes"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Service price"
    )
    sessions_required = models.PositiveIntegerField(
        default=1,
        help_text="Number of sessions required for this service (e.g., Laser = 6, PRP = 3)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the service is currently available"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.duration} min) - ${self.price}"
    
    def requires_multiple_sessions(self):
        """Check if service requires multiple sessions"""
        return self.sessions_required > 1


class StaffMember(models.Model):
    """
    Staff members - standalone model with their own information.
    Not linked to User model for simplicity.
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
    specialization = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Staff specialization or title"
    )
    bio = models.TextField(
        blank=True,
        null=True,
        help_text="Staff bio"
    )
    # Availability schedule
    monday_start = models.TimeField(
        blank=True,
        null=True,
        help_text="Monday start time"
    )
    monday_end = models.TimeField(
        blank=True,
        null=True,
        help_text="Monday end time"
    )
    tuesday_start = models.TimeField(
        blank=True,
        null=True,
        help_text="Tuesday start time"
    )
    tuesday_end = models.TimeField(
        blank=True,
        null=True,
        help_text="Tuesday end time"
    )
    wednesday_start = models.TimeField(
        blank=True,
        null=True,
        help_text="Wednesday start time"
    )
    wednesday_end = models.TimeField(
        blank=True,
        null=True,
        help_text="Wednesday end time"
    )
    thursday_start = models.TimeField(
        blank=True,
        null=True,
        help_text="Thursday start time"
    )
    thursday_end = models.TimeField(
        blank=True,
        null=True,
        help_text="Thursday end time"
    )
    friday_start = models.TimeField(
        blank=True,
        null=True,
        help_text="Friday start time"
    )
    friday_end = models.TimeField(
        blank=True,
        null=True,
        help_text="Friday end time"
    )
    saturday_start = models.TimeField(
        blank=True,
        null=True,
        help_text="Saturday start time"
    )
    saturday_end = models.TimeField(
        blank=True,
        null=True,
        help_text="Saturday end time"
    )
    sunday_start = models.TimeField(
        blank=True,
        null=True,
        help_text="Sunday start time"
    )
    sunday_end = models.TimeField(
        blank=True,
        null=True,
        help_text="Sunday end time"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the staff member is currently active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Staff Member"
        verbose_name_plural = "Staff Members"
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_availability_for_day(self, day_name):
        """Get availability for a specific day (e.g., 'monday', 'tuesday')"""
        start_attr = f"{day_name.lower()}_start"
        end_attr = f"{day_name.lower()}_end"
        start_time = getattr(self, start_attr, None)
        end_time = getattr(self, end_attr, None)
        return start_time, end_time


class Package(models.Model):
    """
    Packages containing multiple services with a fixed number of sessions
    """
    name = models.CharField(
        max_length=200,
        help_text="Package name"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Package description"
    )
    services = models.ManyToManyField(
        Service,
        related_name='packages',
        help_text="Services included in this package (3-5 services)"
    )
    total_sessions = models.PositiveIntegerField(
        help_text="Total number of sessions in this package"
    )
    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Original package price (before discount)"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Package price (after discount)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the package is currently available"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Package"
        verbose_name_plural = "Packages"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.total_sessions} sessions"
    
    def get_discount_percentage(self):
        """Calculate discount percentage"""
        if self.original_price and self.original_price > 0:
            discount = ((self.original_price - self.price) / self.original_price) * 100
            return round(discount, 0)
        return 0
    
    def has_discount(self):
        """Check if package has a discount"""
        return self.original_price and self.original_price > self.price
    
    def clean(self):
        """Validate package has 3-5 services"""
        if self.pk:
            service_count = self.services.count()
            if service_count < 3:
                raise ValidationError("Package must include at least 3 services.")
            if service_count > 5:
                raise ValidationError("Package cannot include more than 5 services.")
    
    def save(self, *args, **kwargs):
        """Override save to run validation after services are set"""
        super().save(*args, **kwargs)
        # Validate after services can be counted
        if self.pk and self.services.exists():
            self.full_clean()


class ClientPackage(models.Model):
    """
    Package assignment to a client with session tracking
    """
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='packages',
        help_text="Client assigned to this package"
    )
    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        related_name='client_assignments',
        help_text="Package assigned"
    )
    sessions_completed = models.PositiveIntegerField(
        default=0,
        help_text="Number of sessions completed"
    )
    is_completed = models.BooleanField(
        default=False,
        help_text="Whether all sessions are completed"
    )
    assigned_date = models.DateField(
        auto_now_add=True,
        help_text="Date when package was assigned"
    )
    completed_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date when package was completed"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes"
    )
    
    class Meta:
        verbose_name = "Client Package"
        verbose_name_plural = "Client Packages"
        ordering = ['-assigned_date']
        unique_together = [['client', 'package']]
    
    def __str__(self):
        return f"{self.client.get_full_name()} - {self.package.name} ({self.sessions_completed}/{self.package.total_sessions})"
    
    def get_progress_percentage(self):
        """Get completion percentage"""
        if self.package.total_sessions == 0:
            return 0
        return int((self.sessions_completed / self.package.total_sessions) * 100)
    
    def add_session(self):
        """Add a completed session"""
        if not self.is_completed:
            self.sessions_completed += 1
            if self.sessions_completed >= self.package.total_sessions:
                self.is_completed = True
                self.completed_date = timezone.now().date()
            self.save()
            return True
        return False
    
    def save(self, *args, **kwargs):
        """Override save to automatically update is_completed status"""
        # Check if sessions are completed
        if self.sessions_completed >= self.package.total_sessions:
            # Mark as completed if not already
            if not self.is_completed:
                self.is_completed = True
                if not self.completed_date:
                    self.completed_date = timezone.now().date()
        else:
            # Mark as not completed if sessions haven't reached total
            if self.is_completed:
                self.is_completed = False
                self.completed_date = None
        super().save(*args, **kwargs)
    
    def get_remaining_sessions(self):
        """Get number of remaining sessions"""
        return max(0, self.package.total_sessions - self.sessions_completed)


class ClientServiceSession(models.Model):
    """
    Tracks individual service sessions for clients
    """
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='service_sessions',
        help_text="Client"
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='client_sessions',
        help_text="Service"
    )
    sessions_completed = models.PositiveIntegerField(
        default=0,
        help_text="Number of sessions completed"
    )
    is_completed = models.BooleanField(
        default=False,
        help_text="Whether all required sessions are completed"
    )
    started_date = models.DateField(
        auto_now_add=True,
        help_text="Date when service sessions started"
    )
    completed_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date when all sessions were completed"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes"
    )
    
    class Meta:
        verbose_name = "Client Service Session"
        verbose_name_plural = "Client Service Sessions"
        ordering = ['-started_date']
        unique_together = [['client', 'service']]
    
    def __str__(self):
        return f"{self.client.get_full_name()} - {self.service.name} ({self.sessions_completed}/{self.service.sessions_required})"
    
    def get_progress_percentage(self):
        """Get completion percentage"""
        if self.service.sessions_required == 0:
            return 0
        return int((self.sessions_completed / self.service.sessions_required) * 100)
    
    def add_session(self):
        """Add a completed session"""
        if not self.is_completed:
            self.sessions_completed += 1
            if self.sessions_completed >= self.service.sessions_required:
                self.is_completed = True
                self.completed_date = timezone.now().date()
            self.save()
            return True
        return False
    
    def save(self, *args, **kwargs):
        """Override save to automatically update is_completed status"""
        # Check if sessions are completed
        if self.sessions_completed >= self.service.sessions_required:
            # Mark as completed if not already
            if not self.is_completed:
                self.is_completed = True
                if not self.completed_date:
                    self.completed_date = timezone.now().date()
        else:
            # Mark as not completed if sessions haven't reached required
            if self.is_completed:
                self.is_completed = False
                self.completed_date = None
        super().save(*args, **kwargs)
    
    def get_remaining_sessions(self):
        """Get number of remaining sessions"""
        return max(0, self.service.sessions_required - self.sessions_completed)


class Appointment(models.Model):
    """
    Appointment bookings
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='appointments',
        help_text="Client who booked the appointment"
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='appointments',
        help_text="Service being booked"
    )
    staff = models.ForeignKey(
        StaffMember,
        on_delete=models.CASCADE,
        related_name='appointments',
        help_text="Staff member assigned to the appointment"
    )
    appointment_date = models.DateField(
        help_text="Date of the appointment"
    )
    appointment_time = models.TimeField(
        help_text="Start time of the appointment"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Appointment status"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes"
    )
    # Link to package or service session tracking
    client_package = models.ForeignKey(
        'ClientPackage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments',
        help_text="Linked package (if session belongs to a package)"
    )
    client_service_session = models.ForeignKey(
        'ClientServiceSession',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments',
        help_text="Linked service session tracking"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
        ordering = ['-appointment_date', '-appointment_time']
        # Prevent double booking: one staff member can't have overlapping appointments
        constraints = [
            models.UniqueConstraint(
                fields=['staff', 'appointment_date', 'appointment_time'],
                name='unique_staff_appointment_time'
            )
        ]
    
    def __str__(self):
        return f"{self.client.get_full_name()} - {self.service.name} - {self.appointment_date} {self.appointment_time}"
    
    def clean(self):
        """Validate appointment to prevent double booking"""
        if self.pk is None:  # Only check for new appointments
            # Calculate end time
            from datetime import timedelta
            start_datetime = timezone.make_aware(
                timezone.datetime.combine(self.appointment_date, self.appointment_time)
            )
            end_datetime = start_datetime + timedelta(minutes=self.service.duration)
            
            # Check for overlapping appointments with the same staff member
            overlapping = Appointment.objects.filter(
                staff=self.staff,
                appointment_date=self.appointment_date,
                status__in=['pending', 'confirmed'],  # Only check active appointments
            ).exclude(pk=self.pk if self.pk else None)
            
            for existing_appt in overlapping:
                existing_start = timezone.make_aware(
                    timezone.datetime.combine(
                        existing_appt.appointment_date,
                        existing_appt.appointment_time
                    )
                )
                existing_end = existing_start + timedelta(minutes=existing_appt.service.duration)
                
                # Check if appointments overlap
                if (start_datetime < existing_end and end_datetime > existing_start):
                    raise ValidationError(
                        f"Appointment overlaps with existing appointment: "
                        f"{existing_appt.appointment_time} - {existing_appt.service.name}"
                    )
    
    def save(self, *args, **kwargs):
        """Override save to run validation and auto-track sessions when completed"""
        self.full_clean()
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Auto-track session when appointment is marked as completed
        if self.status == 'completed' and not is_new:
            # Check if this is a package session
            if self.client_package:
                self.client_package.add_session()
            # Check if this is a service session
            elif self.client_service_session:
                self.client_service_session.add_session()
            # Auto-detect package or service session if not linked
            elif not self.client_package and not self.client_service_session:
                self._auto_track_session()
    
    def _auto_track_session(self):
        """Automatically detect and track package or service sessions"""
        # Check for active packages containing this service
        active_packages = ClientPackage.objects.filter(
            client=self.client,
            package__services=self.service,
            is_completed=False
        )
        
        if active_packages.exists():
            # Assign to the first active package
            package = active_packages.first()
            self.client_package = package
            package.add_session()
            self.save(update_fields=['client_package'])
        else:
            # Check if service requires multiple sessions
            if self.service.sessions_required > 1:
                # Get or create service session tracking
                service_session, created = ClientServiceSession.objects.get_or_create(
                    client=self.client,
                    service=self.service,
                    defaults={'sessions_completed': 0}
                )
                if not service_session.is_completed:
                    service_session.add_session()
                    self.client_service_session = service_session
                    self.save(update_fields=['client_service_session'])
    
    def get_end_time(self):
        """Calculate appointment end time"""
        from datetime import timedelta
        start_datetime = timezone.datetime.combine(self.appointment_date, self.appointment_time)
        end_datetime = start_datetime + timedelta(minutes=self.service.duration)
        return end_datetime.time()
