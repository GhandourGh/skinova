from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.html import format_html
from django.conf import settings
from django import forms
from .models import User, Client


# Hide Groups from admin
admin.site.unregister(Group)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """
    Custom User Admin - Only Admin accounts.
    Admin can do everything except delete their own account.
    """
    list_display = ['username', 'role', 'is_staff', 'is_active', 'last_login']
    list_filter = ['role', 'is_staff', 'is_active']
    fieldsets = (
        (None, {'fields': ('username', 'password', 'role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'current_time')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role', 'is_staff', 'is_active'),
        }),
    )
    readonly_fields = ['last_login', 'current_time']
    
    def current_time(self, obj):
        """Display the current time in Lebanon timezone"""
        # Get current time - Django will use the TIME_ZONE setting (Asia/Beirut)
        now = timezone.localtime(timezone.now())
        # Format: Nov. 23, 2025, 7:26 p.m.
        formatted_time = now.strftime('%b. %d, %Y, %I:%M %p')
        return format_html(
            '<strong style="color: #28a745;">{}</strong>',
            formatted_time
        )
    current_time.short_description = 'Current time (Lebanon)'
    
    def has_module_permission(self, request):
        """Only admin can access Users section"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Admin cannot delete their own account"""
        if obj is None:
            return request.user.is_superuser
        # Prevent admin from deleting themselves
        return request.user.is_superuser and obj != request.user
    
    def delete_model(self, request, obj):
        """Prevent deleting own account"""
        if obj == request.user:
            from django.contrib import messages
            messages.error(request, "You cannot delete your own account.")
            return
        super().delete_model(request, obj)
    
    def delete_queryset(self, request, queryset):
        """Prevent deleting own account from queryset"""
        queryset = queryset.exclude(id=request.user.id)
        super().delete_queryset(request, queryset)


class ClientAdminForm(forms.ModelForm):
    """Custom form for Client admin"""
    class Meta:
        model = Client
        fields = '__all__'


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """
    Client Admin - Staff can add/edit clients, Admin has full access
    """
    form = ClientAdminForm
    list_display = ['get_full_name', 'phone_number', 'view_profile_link', 'created_at']
    list_filter = ['created_at']
    search_fields = ['first_name', 'last_name', 'phone_number']
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'phone_number')
        }),
        ('Additional Information', {
            'fields': ('date_of_birth', 'address', 'notes'),
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
    get_full_name.short_description = 'Full Name'
    
    def get_readonly_fields(self, request, obj=None):
        """Timestamps are always readonly"""
        return self.readonly_fields
    
    def has_delete_permission(self, request, obj=None):
        """Only admin can delete clients"""
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        """Only admin can add clients"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Only admin can edit clients"""
        return request.user.is_superuser
    
    def view_profile_link(self, obj):
        """Link to client profile page"""
        from django.utils.html import format_html
        from django.urls import reverse
        url = reverse('client_profile', args=[obj.id])
        return format_html('<a href="{}" class="button">View Profile</a>', url)
    view_profile_link.short_description = 'Profile'
    
    def changelist_view(self, request, extra_context=None):
        """Add backup management link to changelist"""
        extra_context = extra_context or {}
        from django.urls import reverse
        extra_context['backup_url'] = reverse('backup_management')
        return super().changelist_view(request, extra_context)
    
    def has_module_permission(self, request):
        """Only admin can access Clients module"""
        return request.user.is_superuser
