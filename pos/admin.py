from django.contrib import admin
from .models import Product, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['get_subtotal_display']
    fields = ['product', 'service', 'quantity', 'unit_price', 'get_subtotal_display']
    
    def get_subtotal_display(self, obj):
        """Display subtotal with '$' prefix"""
        if obj.pk:
            return f"${obj.subtotal}"
        return "-"
    get_subtotal_display.short_description = 'Subtotal'
    
    def has_add_permission(self, request, obj=None):
        """Only admin can add order items"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Only admin can edit order items"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Only admin can delete order items"""
        return request.user.is_superuser


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Product Admin - Staff can view products and stock, Admin can edit
    """
    list_display = ['name', 'sku', 'get_price_display', 'stock_qty', 'is_active', 'is_low_stock_display']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'sku', 'description']
    readonly_fields = ['created_at', 'updated_at', 'is_low_stock_display']
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'description', 'sku', 'price', 'is_active')
        }),
        ('Inventory', {
            'fields': ('stock_qty', 'is_low_stock_display')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_price_display(self, obj):
        """Display price with '$' prefix"""
        return f"${obj.price}"
    get_price_display.short_description = 'Price'
    
    def is_low_stock_display(self, obj):
        """Display low stock warning"""
        if obj.is_low_stock():
            return f"⚠️ LOW STOCK ({obj.stock_qty} units)"
        return f"✓ OK ({obj.stock_qty} units)"
    is_low_stock_display.short_description = 'Stock Status'
    
    def get_readonly_fields(self, request, obj=None):
        """Admin can edit everything except timestamps and low stock display"""
        return ['created_at', 'updated_at', 'is_low_stock_display']
    
    def has_delete_permission(self, request, obj=None):
        """Only admin can delete products"""
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        """Only admin can add products"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Only admin can edit products"""
        return request.user.is_superuser
    
    def has_module_permission(self, request):
        """Only admin can access Products module"""
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        """Only admin can view products"""
        return request.user.is_superuser


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Order Admin - Only Admin can manage orders
    """
    list_display = ['id', 'client', 'get_total_price_display', 'payment_method', 'payment_status', 'created_at']
    list_filter = ['payment_method', 'payment_status', 'created_at']
    search_fields = ['client__first_name', 'client__last_name', 'id']
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    readonly_fields = ['total_price', 'created_at', 'updated_at']
    
    def get_total_price_display(self, obj):
        """Display total price with '$' prefix"""
        return f"${obj.total_price}"
    get_total_price_display.short_description = 'Total Price'
    
    fieldsets = (
        ('Order Information', {
            'fields': ('client', 'total_price', 'payment_method', 'payment_status')
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
    
    def get_readonly_fields(self, request, obj=None):
        """Admin can edit everything except timestamps and total_price"""
        return self.readonly_fields
    
    def has_delete_permission(self, request, obj=None):
        """Only admin can delete orders"""
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        """Only admin can add orders"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Only admin can edit orders"""
        return request.user.is_superuser
    
    def has_module_permission(self, request):
        """Only admin can access Orders module"""
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        """Only admin can view orders"""
        return request.user.is_superuser


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Order Item Admin - Only Admin can manage order items
    """
    list_display = ['order', 'product', 'service', 'quantity', 'get_unit_price_display', 'get_subtotal_display']
    list_filter = ['order__created_at']
    readonly_fields = ['subtotal']
    
    def get_unit_price_display(self, obj):
        """Display unit price with '$' prefix"""
        return f"${obj.unit_price}"
    get_unit_price_display.short_description = 'Unit Price'
    
    def get_subtotal_display(self, obj):
        """Display subtotal with '$' prefix"""
        return f"${obj.subtotal}"
    get_subtotal_display.short_description = 'Subtotal'
    
    def has_delete_permission(self, request, obj=None):
        """Only admin can delete order items"""
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        """Only admin can add order items"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Only admin can edit order items"""
        return request.user.is_superuser
