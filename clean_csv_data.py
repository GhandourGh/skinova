import csv
import re
import json

def clean_price(price_str):
    """Extract numeric value from price string like '$50' or '$150'"""
    if not price_str:
        return None
    # Remove $, commas, and whitespace, then extract numbers
    price_str = str(price_str).strip().replace('$', '').replace(',', '').strip()
    # Extract first number found
    match = re.search(r'(\d+(?:\.\d+)?)', price_str)
    if match:
        return float(match.group(1))
    return None

def clean_text(text):
    """Clean and normalize text"""
    if not text:
        return ""
    text = str(text).strip()
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text

def parse_services_csv(filename):
    """Parse and clean the SERVICES.csv file"""
    services = []
    packages = []
    current_service = None
    current_package = None
    in_packages_section = False
    
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    i = 0
    while i < len(rows):
        row = [cell.strip() if cell else "" for cell in rows[i]]
        
        # Skip completely empty rows
        if not any(row):
            i += 1
            continue
        
        # Check if we're entering packages section
        if 'PACKAGES' in str(row[0]).upper():
            in_packages_section = True
            i += 1
            continue
        
        # Parse packages section
        if in_packages_section:
            if row[0] and not row[0].startswith('"') and len(row[0]) > 3 and row[0] not in ['Price', 'Details', 'Products']:
                # New package
                if current_package:
                    packages.append(current_package)
                
                package_name = clean_text(row[0])
                price_str = clean_text(row[1]) if len(row) > 1 else ""
                details = clean_text(row[2]) if len(row) > 2 else ""
                products = clean_text(row[3]) if len(row) > 3 else ""
                
                # Parse price (might be multi-line)
                price = None
                if price_str:
                    price = clean_price(price_str)
                
                current_package = {
                    'name': package_name,
                    'price': price,
                    'price_display': price_str,
                    'details': details,
                    'products': products,
                    'services': []
                }
            elif current_package:
                # Continue reading package details (multi-line)
                if len(row) > 0 and row[0]:
                    # Check if this is a continuation line
                    if not any(cell and len(cell) > 10 for cell in row[1:]):
                        # This might be a continuation of package name or details
                        if len(row) > 2 and row[2]:
                            current_package['details'] += " " + clean_text(row[2])
                        if len(row) > 3 and row[3]:
                            current_package['products'] += " " + clean_text(row[3])
                else:
                    if len(row) > 2 and row[2]:
                        current_package['details'] += " " + clean_text(row[2])
                    if len(row) > 3 and row[3]:
                        current_package['products'] += " " + clean_text(row[3])
        
        # Parse services section
        elif not in_packages_section:
            # Check if this looks like a service row
            first_cell = clean_text(row[0])
            if first_cell and len(first_cell) > 2 and first_cell.upper() not in ['SERVICES NAME', 'PRICE', 'BENEFITS', 'PROCESS']:
                # Check if it's a valid service name (not empty, not just numbers)
                if not first_cell.isdigit() and first_cell not in ['', 'every 7 -15 days', 'DR ELIES + TACHAPRO']:
                    # New service
                    if current_service:
                        services.append(current_service)
                    
                    service_name = first_cell
                    price_str = clean_text(row[1]) if len(row) > 1 else ""
                    benefits = clean_text(row[2]) if len(row) > 2 else ""
                    process = clean_text(row[3]) if len(row) > 3 else ""
                    
                    price = clean_price(price_str)
                    
                    current_service = {
                        'name': service_name,
                        'price': price,
                        'price_display': price_str,
                        'benefits': benefits,
                        'process': process,
                        'duration': None
                    }
            elif current_service:
                # Continue reading service details (multi-line text)
                if len(row) > 2 and row[2]:
                    current_service['benefits'] += " " + clean_text(row[2])
                if len(row) > 3 and row[3]:
                    current_service['process'] += " " + clean_text(row[3])
        
        i += 1
    
    # Don't forget the last service/package
    if current_service:
        services.append(current_service)
    if current_package:
        packages.append(current_package)
    
    return services, packages

def estimate_duration(service_name, process_text):
    """Estimate duration based on service name and process"""
    name_lower = service_name.lower()
    process_lower = process_text.lower() if process_text else ""
    combined = name_lower + " " + process_lower
    
    # Common duration patterns
    if '30-40' in combined or '30--40' in combined:
        return 40
    elif '30' in combined and 'min' in combined:
        return 30
    elif '90' in combined or '90 mins' in combined:
        return 90
    elif 'mini' in name_lower or 'quick' in name_lower:
        return 30
    elif 'meso' in name_lower and 'hair' in name_lower:
        return 30
    elif 'meso' in name_lower and 'lips' in name_lower:
        return 15
    elif 'meso' in name_lower and 'eye' in name_lower:
        return 20
    elif 'meso' in name_lower:
        return 45
    elif 'facial' in name_lower:
        return 60
    elif 'exoglow' in name_lower or 'pdrn' in name_lower:
        return 60
    elif 'carboxy' in name_lower:
        return 40
    elif 'biopeel' in name_lower or 'biorepeel' in name_lower:
        return 45
    else:
        return 45  # Default

def determine_sessions_required(service_name, benefits_text):
    """Determine sessions required based on service info"""
    name_lower = service_name.lower()
    benefits_lower = benefits_text.lower() if benefits_text else ""
    combined = name_lower + " " + benefits_lower
    
    # Services that typically require multiple sessions
    if 'biopeel' in name_lower or 'biorepeel' in name_lower:
        return 4
    elif 'package' in name_lower or 'plan' in name_lower:
        return 1  # Packages are handled separately
    elif '6' in combined and 'session' in combined:
        return 6
    elif '4' in combined and 'session' in combined:
        return 4
    elif '3' in combined and 'session' in combined:
        return 3
    else:
        return 1

# Parse the files
print("Parsing SERVICES.csv...")
services, packages = parse_services_csv('SERVICES.csv')

# Clean and enhance services
cleaned_services = []
for service in services:
    if not service['name'] or service['name'].lower() in ['', 'services name']:
        continue
    
    # Estimate duration if not provided
    if not service.get('duration'):
        service['duration'] = estimate_duration(service['name'], service.get('process', ''))
    
    # Determine sessions required
    service['sessions_required'] = determine_sessions_required(
        service['name'], 
        service.get('benefits', '')
    )
    
    # Combine benefits and process into description
    description_parts = []
    if service.get('benefits'):
        description_parts.append(f"Benefits: {service['benefits']}")
    if service.get('process'):
        description_parts.append(f"Process: {service['process']}")
    
    cleaned_service = {
        'name': service['name'],
        'price': service['price'],
        'duration': service['duration'],
        'sessions_required': service['sessions_required'],
        'description': " | ".join(description_parts) if description_parts else None,
        'is_active': True
    }
    
    cleaned_services.append(cleaned_service)

# Clean packages
cleaned_packages = []
for package in packages:
    if not package['name'] or not package['name'].strip():
        continue
    
    cleaned_package = {
        'name': package['name'],
        'price': package['price'],
        'price_display': package['price_display'],
        'description': package['details'],
        'products': package['products'],
        'total_sessions': None
    }
    
    # Try to extract session count from details
    details = package.get('details', '')
    name_lower = package['name'].lower()
    
    # Count unique weeks mentioned
    week_matches = re.findall(r'week\s*(\d+)', details.lower())
    if week_matches:
        cleaned_package['total_sessions'] = len(set(week_matches))
    else:
        # Count "Week X:" patterns
        week_patterns = re.findall(r'week\s*\d+:', details.lower())
        if week_patterns:
            cleaned_package['total_sessions'] = len(week_patterns)
    
    # Fallback to package name patterns
    if not cleaned_package['total_sessions']:
        if '2 months' in name_lower:
            cleaned_package['total_sessions'] = 8
        elif '1 month' in name_lower or 'month' in name_lower and '2' not in name_lower:
            cleaned_package['total_sessions'] = 4
        elif '6 weeks' in name_lower:
            cleaned_package['total_sessions'] = 6
        elif 'bridal' in name_lower or '3 months' in name_lower:
            cleaned_package['total_sessions'] = 12
        else:
            cleaned_package['total_sessions'] = 4  # Default
    
    cleaned_packages.append(cleaned_package)

# Save cleaned data
output = {
    'services': cleaned_services,
    'packages': cleaned_packages
}

with open('cleaned_data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

# Print summary
print(f"\n✅ Found {len(cleaned_services)} services")
print(f"✅ Found {len(cleaned_packages)} packages")
print("\n📋 Services:")
for s in cleaned_services:
    print(f"  - {s['name']}: ${s['price']} ({s['duration']} min, {s['sessions_required']} sessions)")

print("\n📦 Packages:")
for p in cleaned_packages:
    print(f"  - {p['name']}: ${p['price']} ({p['total_sessions']} sessions)")

print("\n💾 Cleaned data saved to 'cleaned_data.json'")

