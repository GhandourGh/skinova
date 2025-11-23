from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import Service, StaffMember, Appointment, Package, ClientPackage, ClientServiceSession


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """
    Service Admin - Staff can view services, Admin can add/edit/delete
    """
    list_display = ['name', 'get_duration_display', 'get_price_display', 'sessions_required', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    fieldsets = (
        ('Service Details', {
            'fields': ('name', 'description', 'duration', 'price', 'sessions_required', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
    
    def get_duration_display(self, obj):
        """Display duration with 'min' suffix"""
        return f"{obj.duration} min"
    get_duration_display.short_description = 'Duration'
    
    def get_price_display(self, obj):
        """Display price with '$' prefix"""
        return f"${obj.price}"
    get_price_display.short_description = 'Price'
    
    def get_readonly_fields(self, request, obj=None):
        """Admin can edit everything except timestamps"""
        return self.readonly_fields
    
    def has_module_permission(self, request):
        """Only admin can see Services module"""
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        """Only admin can view services"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Only admin can delete services"""
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        """Only admin can add services"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Only admin can edit services"""
        return request.user.is_superuser


class StaffMemberAdminForm(forms.ModelForm):
    """Custom form for StaffMember admin"""
    class Meta:
        model = StaffMember
        fields = '__all__'
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    """
    Staff Member Admin - Standalone model
    Admin has full access, staff can view only
    """
    form = StaffMemberAdminForm
    list_display = ['get_full_name', 'specialization', 'phone_number', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['first_name', 'last_name', 'phone_number', 'specialization']
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'phone_number')
        }),
        ('Professional Information', {
            'fields': ('specialization', 'bio', 'is_active')
        }),
        ('Availability Schedule', {
            'fields': (
                ('monday_start', 'monday_end'),
                ('tuesday_start', 'tuesday_end'),
                ('wednesday_start', 'wednesday_end'),
                ('thursday_start', 'thursday_end'),
                ('friday_start', 'friday_end'),
                ('saturday_start', 'saturday_end'),
                ('sunday_start', 'sunday_end'),
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Name'
    
    def get_readonly_fields(self, request, obj=None):
        """Staff users can only view, admin can edit everything"""
        if not request.user.is_superuser:
            return [f.name for f in self.model._meta.fields if f.name != 'id']
        return self.readonly_fields
    
    def has_delete_permission(self, request, obj=None):
        """Only admin can delete staff members"""
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        """Only admin can add staff members"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Only admin can edit staff members"""
        return request.user.is_superuser
    
    def has_module_permission(self, request):
        """Only admin can see Staff Members module"""
        return request.user.is_superuser


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """
    Appointment Admin - Staff can view, Admin can add/edit/delete
    """
    list_display = ['client', 'service', 'staff', 'appointment_date', 'appointment_time', 'status']
    list_filter = ['status', 'appointment_date', 'service']
    search_fields = ['client__first_name', 'client__last_name', 'service__name', 'staff__first_name']
    date_hierarchy = 'appointment_date'
    fieldsets = (
        ('Appointment Details', {
            'fields': ('client', 'service', 'staff', 'appointment_date', 'appointment_time', 'status')
        }),
        ('Session Tracking', {
            'fields': ('client_package', 'client_service_session'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
    
    def get_readonly_fields(self, request, obj=None):
        """Admin can edit everything except timestamps"""
        return self.readonly_fields
    
    def has_module_permission(self, request):
        """Only admin can see Appointments module"""
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        """Only admin can view appointments"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Only admin can delete appointments"""
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        """Only admin can add appointments"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Only admin can edit appointments"""
        return request.user.is_superuser


class PackageServiceInline(admin.TabularInline):
    """Inline for services in Package"""
    model = Package.services.through
    extra = 1
    verbose_name = "Service"
    verbose_name_plural = "Services"


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    """
    Package Admin - Staff can view, Admin can add/edit/delete
    """
    list_display = ['name', 'total_sessions', 'get_price_display', 'get_service_count', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    inlines = [PackageServiceInline]
    fieldsets = (
        ('Package Details', {
            'fields': ('name', 'description', 'total_sessions', 'original_price', 'price', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
    
    def get_service_count(self, obj):
        return obj.services.count()
    get_service_count.short_description = 'Services'
    
    def get_price_display(self, obj):
        """Display price with original price strikethrough if discount exists"""
        if obj.has_discount():
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">${}</span> <strong style="color: #d32f2f;">${}</strong>',
                obj.original_price,
                obj.price
            )
        return f'${obj.price}'
    get_price_display.short_description = 'Price'
    
    def get_readonly_fields(self, request, obj=None):
        """Admin can edit everything except timestamps"""
        return self.readonly_fields
    
    def has_module_permission(self, request):
        """Only admin can see Packages module"""
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        """Only admin can view packages"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(ClientPackage)
class ClientPackageAdmin(admin.ModelAdmin):
    """
    Client Package Admin - Admin can manage, staff can view
    """
    list_display = ['client', 'package', 'sessions_completed', 'get_total_sessions', 'is_completed', 'assigned_date']
    list_filter = ['is_completed', 'assigned_date', 'package']
    search_fields = ['client__first_name', 'client__last_name', 'package__name']
    readonly_fields = ['assigned_date']
    fieldsets = (
        ('Assignment Details', {
            'fields': ('client', 'package', 'sessions_completed', 'is_completed')
        }),
        ('Dates', {
            'fields': ('assigned_date', 'completed_date'),
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def get_total_sessions(self, obj):
        return obj.package.total_sessions
    get_total_sessions.short_description = 'Total Sessions'
    
    def get_readonly_fields(self, request, obj=None):
        """Admin can edit everything except assigned_date"""
        readonly = ['assigned_date']  # Always readonly since auto_now_add=True
        return readonly
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Only admin can edit client packages"""
        return request.user.is_superuser
    
    def has_module_permission(self, request):
        """Only admin can see Client Packages module"""
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        """Only admin can view client packages"""
        return request.user.is_superuser


@admin.register(ClientServiceSession)
class ClientServiceSessionAdmin(admin.ModelAdmin):
    """
    Client Service Session Admin - Admin can manage, staff can view
    """
    list_display = ['client', 'service', 'sessions_completed', 'get_required_sessions', 'is_completed', 'started_date']
    list_filter = ['is_completed', 'started_date', 'service']
    search_fields = ['client__first_name', 'client__last_name', 'service__name']
    readonly_fields = ['started_date']
    fieldsets = (
        ('Session Details', {
            'fields': ('client', 'service', 'sessions_completed', 'is_completed')
        }),
        ('Dates', {
            'fields': ('started_date', 'completed_date'),
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def get_required_sessions(self, obj):
        return obj.service.sessions_required
    get_required_sessions.short_description = 'Required Sessions'
    
    def get_readonly_fields(self, request, obj=None):
        """Admin can edit everything except started_date"""
        readonly = ['started_date']  # Always readonly since auto_now_add=True
        return readonly
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Only admin can edit client service sessions"""
        return request.user.is_superuser
    
    def has_module_permission(self, request):
        """Only admin can see Client Service Sessions module"""
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        """Only admin can view client service sessions"""
        return request.user.is_superuser
