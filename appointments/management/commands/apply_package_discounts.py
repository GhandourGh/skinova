"""
Management command to apply 20% discount to all packages
Run with: python manage.py apply_package_discounts
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction

from appointments.models import Package


class Command(BaseCommand):
    help = 'Applies 20% discount to all packages (sets original_price and updates price)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--discount',
            type=float,
            default=20.0,
            help='Discount percentage (default: 20.0)',
        )

    def handle(self, *args, **options):
        discount_percentage = options['discount']
        discount_multiplier = Decimal(str(1 - (discount_percentage / 100)))
        
        self.stdout.write(self.style.SUCCESS(f'Applying {discount_percentage}% discount to all packages...'))
        
        with transaction.atomic():
            packages_updated = 0
            
            for package in Package.objects.all():
                # If original_price is not set, use current price as original
                if not package.original_price:
                    package.original_price = package.price
                
                # Calculate discounted price
                new_price = package.original_price * discount_multiplier
                new_price = new_price.quantize(Decimal('0.01'))  # Round to 2 decimal places
                
                old_price = package.price
                package.price = new_price
                package.save()
                
                packages_updated += 1
                self.stdout.write(
                    f'  ✓ {package.name}: '
                    f'${package.original_price} → ${package.price} '
                    f'(saved ${package.original_price - package.price})'
                )
            
            self.stdout.write(self.style.SUCCESS(f'\n✅ Updated {packages_updated} packages with {discount_percentage}% discount!'))

