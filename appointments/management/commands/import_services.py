"""
Management command to import services and packages from cleaned CSV data
Run with: python manage.py import_services
"""
import json
import re
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction

from appointments.models import Service, Package


class Command(BaseCommand):
    help = 'Imports services and packages from cleaned_data.json'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing services and packages before importing',
        )
        parser.add_argument(
            '--file',
            type=str,
            default='cleaned_data.json',
            help='Path to the cleaned data JSON file',
        )

    def find_services_in_text(self, text, all_services):
        """Find service names mentioned in text"""
        found_services = []
        text_lower = text.lower()
        
        for service in all_services:
            service_name_lower = service.name.lower()
            # Try to match service name in text
            # Remove common words and check for key terms
            key_terms = []
            for word in service_name_lower.split():
                if len(word) > 3:  # Skip short words
                    key_terms.append(word)
            
            # Check if key terms appear in text
            matches = sum(1 for term in key_terms if term in text_lower)
            if matches >= 2 or (len(key_terms) == 1 and key_terms[0] in text_lower):
                found_services.append(service)
        
        return found_services

    def calculate_package_price(self, package_data, all_services):
        """Calculate package price from description if not provided"""
        if package_data.get('price'):
            return Decimal(str(package_data['price']))
        
        # Try to extract from description
        description = package_data.get('description', '').lower()
        
        # Look for price patterns like "$50", "$150", etc.
        price_matches = re.findall(r'\$(\d+)', package_data.get('description', ''))
        if price_matches:
            total = sum(int(p) for p in price_matches)
            return Decimal(str(total))
        
        # For HAIR TREATMENT PLAN specifically
        if 'hair treatment' in package_data['name'].lower():
            # 3 hair meso $120 + 3 hair exosomes $450 = $570
            return Decimal('570.00')
        
        return None

    def handle(self, *args, **options):
        file_path = options['file']
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File {file_path} not found!'))
            return
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'Error parsing JSON: {e}'))
            return

        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing services and packages...'))
            Package.objects.all().delete()
            Service.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared!'))

        self.stdout.write(self.style.SUCCESS('Importing services and packages...'))

        with transaction.atomic():
            # Import Services
            services_created = 0
            services_updated = 0
            service_map = {}  # Map service names to Service objects
            
            for service_data in data.get('services', []):
                name = service_data['name'].strip()
                if not name:
                    continue
                
                price = Decimal(str(service_data['price'])) if service_data.get('price') else Decimal('0.00')
                duration = service_data.get('duration', 45)
                sessions_required = service_data.get('sessions_required', 1)
                description = service_data.get('description', '')
                is_active = service_data.get('is_active', True)
                
                service, created = Service.objects.update_or_create(
                    name=name,
                    defaults={
                        'price': price,
                        'duration': duration,
                        'sessions_required': sessions_required,
                        'description': description,
                        'is_active': is_active,
                    }
                )
                
                service_map[name] = service
                
                if created:
                    services_created += 1
                    self.stdout.write(f'  ✓ Created service: {name} (${price})')
                else:
                    services_updated += 1
                    self.stdout.write(f'  ↻ Updated service: {name} (${price})')

            self.stdout.write(self.style.SUCCESS(f'\n✅ Imported {services_created} new services, updated {services_updated} existing'))

            # Import Packages
            packages_created = 0
            packages_updated = 0
            
            for package_data in data.get('packages', []):
                name = package_data['name'].strip()
                if not name:
                    continue
                
                # Calculate price if not provided
                price = self.calculate_package_price(package_data, list(service_map.values()))
                if not price:
                    self.stdout.write(self.style.WARNING(f'  ⚠ Package {name} has no price - skipping'))
                    continue
                
                description = package_data.get('description', '')
                if package_data.get('products'):
                    if description:
                        description += f"\n\nProducts included: {package_data['products']}"
                    else:
                        description = f"Products included: {package_data['products']}"
                
                total_sessions = package_data.get('total_sessions', 4)
                is_active = True
                
                # Set original_price to the imported price, then apply 20% discount
                original_price = price
                discounted_price = price * Decimal('0.8')  # 20% discount
                discounted_price = discounted_price.quantize(Decimal('0.01'))  # Round to 2 decimals
                
                package, created = Package.objects.update_or_create(
                    name=name,
                    defaults={
                        'original_price': original_price,
                        'price': discounted_price,
                        'description': description,
                        'total_sessions': total_sessions,
                        'is_active': is_active,
                    }
                )
                
                # Try to find and link services from description
                found_services = self.find_services_in_text(description, list(service_map.values()))
                
                # Also try to find services by common patterns in package names
                package_name_lower = name.lower()
                if 'hair' in package_name_lower:
                    if 'HAIR MESO' in service_map:
                        found_services.append(service_map['HAIR MESO'])
                    if 'EXOHAIR' in service_map:
                        found_services.append(service_map['EXOHAIR'])
                if 'skin booster' in package_name_lower or 'skin reset' in package_name_lower:
                    if 'MESO SKIN BOOSTER' in service_map:
                        found_services.append(service_map['MESO SKIN BOOSTER'])
                    if 'EXOGLOW + PDRN' in service_map:
                        found_services.append(service_map['EXOGLOW + PDRN'])
                    if 'DEEP GLOW FACIAL' in service_map or 'DIAMOND INFUSION FACIAL' in service_map:
                        # Try to find hydrafacial
                        for key in ['DEEP GLOW FACIAL', 'DIAMOND INFUSION FACIAL', 'DETOX FACIAL']:
                            if key in service_map:
                                found_services.append(service_map[key])
                                break
                if 'cellulite' in package_name_lower:
                    if 'ANTI CELLULITE' in service_map:
                        found_services.append(service_map['ANTI CELLULITE'])
                if 'whitening' in package_name_lower or 'knee' in package_name_lower:
                    if 'KNEE WHITENING' in service_map:
                        found_services.append(service_map['KNEE WHITENING'])
                    if 'UNDERARM GLOW' in service_map:
                        found_services.append(service_map['UNDERARM GLOW'])
                if 'bridal' in package_name_lower:
                    # VIP Bridal has many services
                    for key in service_map.keys():
                        if any(term in key.lower() for term in ['facial', 'meso', 'exoglow', 'pdrn', 'underarm', 'co2']):
                            if service_map[key] not in found_services:
                                found_services.append(service_map[key])
                
                # Remove duplicates
                found_services = list(set(found_services))
                
                # Ensure we have 3-5 services (package requirement)
                if len(found_services) < 3:
                    self.stdout.write(self.style.WARNING(
                        f'  ⚠ Package {name} has only {len(found_services)} services found. '
                        f'Adding common services to meet minimum requirement.'
                    ))
                    # Add some common services if we don't have enough
                    common_services = [s for s in service_map.values() if s not in found_services]
                    while len(found_services) < 3 and common_services:
                        found_services.append(common_services.pop(0))
                
                if len(found_services) > 5:
                    found_services = found_services[:5]
                    self.stdout.write(self.style.WARNING(
                        f'  ⚠ Package {name} has more than 5 services. Using first 5.'
                    ))
                
                # Set the services
                package.services.set(found_services)
                
                if created:
                    packages_created += 1
                    self.stdout.write(f'  ✓ Created package: {name} (${price}, {len(found_services)} services)')
                else:
                    packages_updated += 1
                    self.stdout.write(f'  ↻ Updated package: {name} (${price}, {len(found_services)} services)')

            self.stdout.write(self.style.SUCCESS(f'\n✅ Imported {packages_created} new packages, updated {packages_updated} existing'))
            self.stdout.write(self.style.SUCCESS('\n🎉 Import completed successfully!'))

