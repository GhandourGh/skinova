from django.db import models
from django.core.exceptions import ValidationError
from core.models import Client
from appointments.models import Service, Appointment


class Product(models.Model):
    """
    Products sold in the POS system (skincare products, etc.)
    """
    name = models.CharField(
        max_length=200,
        help_text="Product name"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Product description"
    )
    sku = models.CharField(
        max_length=100,
        unique=True,
        help_text="Stock Keeping Unit (SKU) code"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Product price"
    )
    stock_qty = models.PositiveIntegerField(
        default=0,
        help_text="Current stock quantity"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the product is currently available for sale"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} (SKU: {self.sku}) - ${self.price}"
    
    def is_low_stock(self, threshold=5):
        """Check if product is low in stock"""
        return self.stock_qty < threshold


class Order(models.Model):
    """
    POS Orders/Transactions
    """
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('credit', 'Credit'),
        ('other', 'Other'),
    ]
    
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        help_text="Client who made the purchase (optional for walk-ins)"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total order amount"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash',
        help_text="Payment method used"
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('paid', 'Paid'), ('refunded', 'Refunded')],
        default='paid',
        help_text="Payment status"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Order notes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']
    
    def __str__(self):
        client_name = self.client.get_full_name() if self.client else "Walk-in"
        return f"Order #{self.pk} - {client_name} - ${self.total_price}"


class OrderItem(models.Model):
    """
    Individual items in an order (can be Product or Service)
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Parent order"
    )
    # Product reference (optional - order item can be a product)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='order_items',
        help_text="Product being ordered (if applicable)"
    )
    # Service reference (optional - order item can be a service)
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='order_items',
        help_text="Service being ordered (if applicable)"
    )
    # Appointment reference (optional - if service is linked to an appointment)
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items',
        help_text="Linked appointment (if service was booked)"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        help_text="Quantity ordered"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per unit at time of sale"
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Line item total (quantity * unit_price)"
    )
    
    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        ordering = ['order', 'id']
    
    def __str__(self):
        item_name = self.product.name if self.product else self.service.name
        return f"{item_name} x{self.quantity} - ${self.subtotal}"
    
    def clean(self):
        """Validate that exactly one of product or service is set"""
        if not self.product and not self.service:
            raise ValidationError("Order item must have either a product or a service.")
        if self.product and self.service:
            raise ValidationError("Order item cannot have both a product and a service.")
        
        # If service is provided, validate appointment link if applicable
        if self.service and self.appointment:
            if self.appointment.service != self.service:
                raise ValidationError("Appointment service must match order item service.")
    
    def save(self, *args, **kwargs):
        """Override save to run validation and calculate subtotal"""
        self.full_clean()
        
        # Calculate subtotal
        self.subtotal = self.quantity * self.unit_price
        
        super().save(*args, **kwargs)
        
        # Update order total
        if self.order:
            self.order.total_price = sum(item.subtotal for item in self.order.items.all())
            self.order.save()
        
        # If this is a service with an appointment, mark appointment as completed on checkout
        # This will be handled in the checkout view logic
