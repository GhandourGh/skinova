from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, FileResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.management import call_command
from django.conf import settings
from datetime import datetime
from pathlib import Path
import os
import zipfile
import io
from .models import Client
from appointments.models import ClientPackage, ClientServiceSession, Package, Service


@login_required
def client_profile(request, client_id):
    """Client profile page with packages and service sessions"""
    client = get_object_or_404(Client, id=client_id)
    
    # Get active packages
    client_packages = ClientPackage.objects.filter(client=client).select_related('package').prefetch_related('package__services')
    
    # Get active service sessions (services with multiple sessions required)
    service_sessions = ClientServiceSession.objects.filter(client=client).select_related('service')
    
    # Get available packages for assignment (only show packages not already assigned)
    assigned_package_ids = client_packages.values_list('package_id', flat=True)
    available_packages = Package.objects.filter(is_active=True).exclude(id__in=assigned_package_ids).prefetch_related('services')
    
    # Get available services for assignment (active services)
    # We can filter out services already being tracked if desired, or allow multiple
    available_services = Service.objects.filter(is_active=True)
    
    context = {
        'client': client,
        'client_packages': client_packages,
        'service_sessions': service_sessions,
        'available_packages': available_packages,
        'available_services': available_services,
    }
    
    return render(request, 'core/client_profile.html', context)


@login_required
@require_POST
def add_package_session(request, client_package_id):
    """Add a session to a client package"""
    try:
        client_package = get_object_or_404(ClientPackage, id=client_package_id)
        
        if client_package.is_completed:
            messages.warning(request, 'This package is already completed.')
            return redirect('client_profile', client_id=client_package.client.id)
        
        success = client_package.add_session()
        
        if success:
            # Refresh from database to get updated values
            client_package.refresh_from_db()
            messages.success(request, f'Session added! Progress: {client_package.sessions_completed}/{client_package.package.total_sessions}')
            if client_package.is_completed:
                messages.info(request, 'Package completed!')
        else:
            messages.error(request, 'Could not add session.')
    except Exception as e:
        messages.error(request, f'Error adding session: {str(e)}')
        # Try to get client_id even if there's an error
        try:
            client_package = ClientPackage.objects.get(id=client_package_id)
            return redirect('client_profile', client_id=client_package.client.id)
        except:
            return redirect('admin:index')
    
    return redirect('client_profile', client_id=client_package.client.id)


@login_required
@require_POST
def add_service_session(request, service_session_id):
    """Add a session to a client service"""
    try:
        service_session = get_object_or_404(ClientServiceSession, id=service_session_id)
        
        if service_session.is_completed:
            messages.warning(request, 'This service is already completed.')
            return redirect('client_profile', client_id=service_session.client.id)
        
        success = service_session.add_session()
        
        if success:
            # Refresh from database to get updated values
            service_session.refresh_from_db()
            messages.success(request, f'Session added! Progress: {service_session.sessions_completed}/{service_session.service.sessions_required}')
            if service_session.is_completed:
                messages.info(request, 'Service completed!')
        else:
            messages.error(request, 'Could not add session.')
    except Exception as e:
        messages.error(request, f'Error adding session: {str(e)}')
        # Try to get client_id even if there's an error
        try:
            service_session = ClientServiceSession.objects.get(id=service_session_id)
            return redirect('client_profile', client_id=service_session.client.id)
        except:
            return redirect('admin:index')
    
    return redirect('client_profile', client_id=service_session.client.id)


@login_required
@require_POST
def assign_package_to_client(request, client_id):
    """Assign a package to a client"""
    client = get_object_or_404(Client, id=client_id)
    package_id = request.POST.get('package_id')
    
    if not package_id:
        messages.error(request, 'Please select a package.')
        return redirect('client_profile', client_id=client.id)
    
    # Validate package_id is numeric
    try:
        package_id = int(package_id)
    except (ValueError, TypeError):
        messages.error(request, 'Invalid package selection.')
        return redirect('client_profile', client_id=client.id)
    
    try:
        package = Package.objects.get(id=package_id, is_active=True)
    except Package.DoesNotExist:
        messages.error(request, 'Selected package not found or inactive.')
        return redirect('client_profile', client_id=client.id)
    
    # Check if package already assigned
    if ClientPackage.objects.filter(client=client, package=package).exists():
        messages.warning(request, 'Package is already assigned to this client.')
        return redirect('client_profile', client_id=client.id)
    
    # Create assignment
    try:
        ClientPackage.objects.create(
            client=client,
            package=package,
            sessions_completed=0,
            is_completed=False
        )
        messages.success(request, f'Package "{package.name}" assigned successfully!')
    except Exception as e:
        messages.error(request, f'Error assigning package: {str(e)}')
    
    return redirect('client_profile', client_id=client.id)


@login_required
@require_POST
def start_service_session(request, client_id):
    """Start tracking a service session for a client"""
    client = get_object_or_404(Client, id=client_id)
    service_id = request.POST.get('service_id')
    
    if not service_id:
        messages.error(request, 'Please select a service.')
        return redirect('client_profile', client_id=client.id)
    
    # Validate service_id is numeric
    try:
        service_id = int(service_id)
    except (ValueError, TypeError):
        messages.error(request, 'Invalid service selection.')
        return redirect('client_profile', client_id=client.id)
    
    from appointments.models import Service
    try:
        service = Service.objects.get(id=service_id, is_active=True)
    except Service.DoesNotExist:
        messages.error(request, 'Selected service not found or inactive.')
        return redirect('client_profile', client_id=client.id)
    
    # Create new session tracking (allow duplicates)
    try:
        service_session = ClientServiceSession.objects.create(
            client=client,
            service=service,
            sessions_completed=0,
            is_completed=False
        )
        
        messages.success(request, f'Started tracking "{service.name}" sessions!')
    except Exception as e:
        messages.error(request, f'Error starting service session: {str(e)}')
    
    return redirect('client_profile', client_id=client.id)


@login_required
@require_POST
def adjust_session_count(request, item_type, item_id):
    """Adjust session count (increment/decrement)"""
    action = request.POST.get('action')
    client_id = None
    
    try:
        if item_type == 'package':
            item = get_object_or_404(ClientPackage, id=item_id)
            total_sessions = item.package.total_sessions
        elif item_type == 'service':
            item = get_object_or_404(ClientServiceSession, id=item_id)
            total_sessions = item.service.sessions_required
        else:
            return redirect('admin:index')
            
        client_id = item.client.id
        
        if action == 'increment':
            # Use the model's add_session method if available, or manual logic
            if hasattr(item, 'add_session'):
                if not item.is_completed:
                    item.add_session()
                    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        messages.success(request, 'Session added.')
                else:
                    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        messages.warning(request, 'Already completed.')
            else:
                # Manual increment if no method (fallback)
                if item.sessions_completed < total_sessions:
                    item.sessions_completed += 1
                    if item.sessions_completed >= total_sessions:
                        item.is_completed = True
                        item.completed_date = datetime.now().date()
                    item.save()
                    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        messages.success(request, 'Session added.')
                    
        elif action == 'decrement':
            if item.sessions_completed > 0:
                item.sessions_completed -= 1
                item.is_completed = False
                item.completed_date = None
                item.save()
                if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    messages.success(request, 'Session removed.')
            else:
                if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    messages.warning(request, 'Cannot go below 0.')
        
        # If AJAX request, return JSON with new state
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            item.refresh_from_db()
            return JsonResponse({
                'success': True,
                'sessions_completed': item.sessions_completed,
                'total_sessions': total_sessions,
                'is_completed': item.is_completed,
                'progress_percentage': item.get_progress_percentage(),
                'completed_date': item.completed_date.strftime('%b %d, %Y') if item.completed_date else None,
                'assigned_date': item.assigned_date.strftime('%b %d, %Y') if hasattr(item, 'assigned_date') else None,
                'started_date': item.started_date.strftime('%b %d, %Y') if hasattr(item, 'started_date') else None,
            })
                
    except Exception as e:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        messages.error(request, f'Error adjusting session: {str(e)}')
        if client_id:
            return redirect('client_profile', client_id=client_id)
        return redirect('admin:index')
    
    return redirect('client_profile', client_id=client_id)


@login_required
@require_POST
def delete_service_session(request, service_session_id):
    """Delete a client service session"""
    try:
        service_session = get_object_or_404(ClientServiceSession, id=service_session_id)
        client_id = service_session.client.id
        service_name = service_session.service.name
        service_session.delete()
        messages.success(request, f'Removed service "{service_name}" from client.')
    except Exception as e:
        messages.error(request, f'Error removing service: {str(e)}')
        # Try to redirect back to client profile if possible
        if 'client_id' in locals():
            return redirect('client_profile', client_id=client_id)
        return redirect('admin:index')
    
    return redirect('client_profile', client_id=client_id)


@login_required
@require_POST
def delete_client_package(request, client_package_id):
    """Delete a client package assignment"""
    try:
        client_package = get_object_or_404(ClientPackage, id=client_package_id)
        client_id = client_package.client.id
        package_name = client_package.package.name
        client_package.delete()
        messages.success(request, f'Removed package "{package_name}" from client.')
    except Exception as e:
        messages.error(request, f'Error removing package: {str(e)}')
        if 'client_id' in locals():
            return redirect('client_profile', client_id=client_id)
        return redirect('admin:index')
    
    return redirect('client_profile', client_id=client_id)


@login_required
def backup_management(request):
    """Backup management page"""
    if not request.user.is_superuser:
        messages.error(request, 'Only administrators can access backup management.')
        return redirect('admin:index')
    
    # List existing backups
    backups_dir = Path(settings.BASE_DIR) / 'backups'
    backups_dir.mkdir(exist_ok=True)
    
    backups = []
    if backups_dir.exists():
        for backup_file in sorted(backups_dir.glob('skinova_backup_*.zip'), reverse=True):
            stat = backup_file.stat()
            backups.append({
                'name': backup_file.name,
                'size': stat.st_size / (1024 * 1024),  # MB
                'created': datetime.fromtimestamp(stat.st_mtime),
                'path': str(backup_file),
            })
    
    context = {
        'backups': backups,
    }
    return render(request, 'core/backup_management.html', context)


@login_required
@require_POST
def create_backup(request):
    """Create a new backup"""
    if not request.user.is_superuser:
        messages.error(request, 'Only administrators can create backups.')
        return redirect('admin:index')
    
    try:
        from django.core.management import call_command
        from io import StringIO
        import sys
        
        # Capture output
        output = StringIO()
        old_stdout = sys.stdout
        sys.stdout = output
        
        try:
            call_command('backup_system', verbosity=1)
            output_str = output.getvalue()
            # Extract backup filename from output if possible
            messages.success(request, 'Backup created successfully! Check the backups list to download it.')
        finally:
            sys.stdout = old_stdout
        
        return redirect('backup_management')
    except Exception as e:
        messages.error(request, f'Error creating backup: {str(e)}')
        return redirect('backup_management')


@login_required
def download_backup(request, backup_name):
    """Download a backup file"""
    if not request.user.is_superuser:
        messages.error(request, 'Only administrators can download backups.')
        return redirect('admin:index')
    
    # Security: Prevent path traversal attacks
    # Only allow alphanumeric, dash, underscore, and dot characters
    import re
    if not re.match(r'^[a-zA-Z0-9._-]+\.zip$', backup_name):
        messages.error(request, 'Invalid backup filename.')
        return redirect('backup_management')
    
    backups_dir = Path(settings.BASE_DIR) / 'backups'
    backup_path = backups_dir / backup_name
    
    # Additional security: Ensure the resolved path is within backups directory
    try:
        backup_path = backup_path.resolve()
        backups_dir = backups_dir.resolve()
        if not str(backup_path).startswith(str(backups_dir)):
            messages.error(request, 'Invalid backup path.')
            return redirect('backup_management')
    except (OSError, ValueError):
        messages.error(request, 'Invalid backup path.')
        return redirect('backup_management')
    
    if not backup_path.exists() or not backup_path.is_file():
        messages.error(request, 'Backup file not found.')
        return redirect('backup_management')
    
    # Properly handle file with context manager
    file_handle = open(backup_path, 'rb')
    response = FileResponse(
        file_handle,
        as_attachment=True,
        filename=backup_name
    )
    # FileResponse will close the file when response is finished
    return response


@login_required
@require_POST
def delete_backup(request, backup_name):
    """Delete a backup file"""
    if not request.user.is_superuser:
        messages.error(request, 'Only administrators can delete backups.')
        return redirect('admin:index')
    
    # Security: Prevent path traversal attacks
    import re
    if not re.match(r'^[a-zA-Z0-9._-]+\.zip$', backup_name):
        messages.error(request, 'Invalid backup filename.')
        return redirect('backup_management')
    
    backups_dir = Path(settings.BASE_DIR) / 'backups'
    backup_path = backups_dir / backup_name
    
    # Additional security: Ensure the resolved path is within backups directory
    try:
        backup_path = backup_path.resolve()
        backups_dir = backups_dir.resolve()
        if not str(backup_path).startswith(str(backups_dir)):
            messages.error(request, 'Invalid backup path.')
            return redirect('backup_management')
    except (OSError, ValueError):
        messages.error(request, 'Invalid backup path.')
        return redirect('backup_management')
    
    if backup_path.exists() and backup_path.is_file():
        try:
            backup_path.unlink()
            messages.success(request, f'Backup {backup_name} deleted successfully.')
        except OSError as e:
            messages.error(request, f'Error deleting backup: {str(e)}')
    else:
        messages.error(request, 'Backup file not found.')
    
    return redirect('backup_management')
