"""
Management command to create a complete backup of the Skinova Clinic system
Run with: python manage.py backup_system
Creates a zip file with database, media files, static files, and data export
"""
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import io
import sys


class Command(BaseCommand):
    help = 'Creates a complete backup of the Skinova Clinic system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='backups',
            help='Directory to save backup files (default: backups)',
        )
        parser.add_argument(
            '--include-media',
            action='store_true',
            default=True,
            help='Include media files in backup (default: True)',
        )
        parser.add_argument(
            '--include-static',
            action='store_true',
            default=True,
            help='Include static files in backup (default: True)',
        )

    def handle(self, *args, **options):
        output_dir = Path(options['output_dir'])
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_name = f'skinova_backup_{timestamp}'
        backup_path = output_dir / f'{backup_name}.zip'
        
        self.stdout.write(self.style.SUCCESS(f'\n🔄 Creating backup: {backup_name}'))
        
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 1. Backup Database
                self.stdout.write('  📦 Backing up database...')
                db_path = Path(settings.DATABASES['default']['NAME'])
                if db_path.exists():
                    zipf.write(db_path, f'database/{db_path.name}')
                    self.stdout.write(self.style.SUCCESS(f'    ✓ Database backed up ({db_path.name})'))
                else:
                    self.stdout.write(self.style.WARNING('    ⚠ Database file not found'))
                
                # 2. Export Data to JSON
                self.stdout.write('  📄 Exporting data to JSON...')
                json_output = io.StringIO()
                try:
                    call_command('dumpdata', 
                               '--natural-foreign', 
                               '--natural-primary',
                               '--exclude', 'contenttypes',
                               '--exclude', 'auth.permission',
                               '--exclude', 'admin.logentry',
                               '--exclude', 'sessions.session',
                               stdout=json_output)
                    json_data = json_output.getvalue()
                    zipf.writestr('data_export.json', json_data)
                    self.stdout.write(self.style.SUCCESS('    ✓ Data exported to JSON'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'    ✗ Error exporting data: {e}'))
                
                # 3. Backup Media Files
                if options['include_media']:
                    self.stdout.write('  🖼️  Backing up media files...')
                    media_root = Path(settings.MEDIA_ROOT)
                    if media_root.exists():
                        media_count = 0
                        for root, dirs, files in os.walk(media_root):
                            for file in files:
                                file_path = Path(root) / file
                                arcname = f'media/{file_path.relative_to(media_root)}'
                                zipf.write(file_path, arcname)
                                media_count += 1
                        self.stdout.write(self.style.SUCCESS(f'    ✓ {media_count} media files backed up'))
                    else:
                        self.stdout.write(self.style.WARNING('    ⚠ Media directory not found'))
                
                # 4. Backup Static Files (images, custom CSS)
                if options['include_static']:
                    self.stdout.write('  🎨 Backing up static files...')
                    static_dirs = [
                        Path(settings.BASE_DIR) / 'static',
                        Path(settings.BASE_DIR) / 'images',
                    ]
                    static_count = 0
                    for static_dir in static_dirs:
                        if static_dir.exists():
                            for root, dirs, files in os.walk(static_dir):
                                for file in files:
                                    file_path = Path(root) / file
                                    # Skip __pycache__ and other unnecessary files
                                    if '__pycache__' in str(file_path) or file.endswith('.pyc'):
                                        continue
                                    arcname = f'static/{file_path.relative_to(static_dir.parent)}'
                                    zipf.write(file_path, arcname)
                                    static_count += 1
                    if static_count > 0:
                        self.stdout.write(self.style.SUCCESS(f'    ✓ {static_count} static files backed up'))
                    else:
                        self.stdout.write(self.style.WARNING('    ⚠ No static files found'))
                
                # 5. Backup Requirements
                self.stdout.write('  📋 Backing up requirements...')
                requirements_path = Path(settings.BASE_DIR) / 'requirements.txt'
                if requirements_path.exists():
                    zipf.write(requirements_path, 'requirements.txt')
                    self.stdout.write(self.style.SUCCESS('    ✓ Requirements backed up'))
                
                # 6. Create backup info file
                backup_info = f"""Skinova Clinic System Backup
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Django Version: {settings.__dict__.get('__version__', 'Unknown')}
Database: {settings.DATABASES['default']['ENGINE']}

Contents:
- Database: {db_path.name if db_path.exists() else 'Not found'}
- Data Export: data_export.json
- Media Files: {'Included' if options['include_media'] else 'Excluded'}
- Static Files: {'Included' if options['include_static'] else 'Excluded'}
- Requirements: requirements.txt

To restore this backup, run:
python manage.py restore_system {backup_path.name}
"""
                zipf.writestr('BACKUP_INFO.txt', backup_info)
            
            file_size = backup_path.stat().st_size / (1024 * 1024)  # Size in MB
            self.stdout.write(self.style.SUCCESS(f'\n✅ Backup created successfully!'))
            self.stdout.write(self.style.SUCCESS(f'   Location: {backup_path}'))
            self.stdout.write(self.style.SUCCESS(f'   Size: {file_size:.2f} MB'))
            self.stdout.write(self.style.SUCCESS(f'\n💾 Save this file to transfer to another system!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error creating backup: {e}'))
            if backup_path.exists():
                backup_path.unlink()
            raise

