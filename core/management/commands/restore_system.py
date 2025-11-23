"""
Management command to restore a complete backup of the Skinova Clinic system
Run with: python manage.py restore_system backup_file.zip
"""
import os
import shutil
import zipfile
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings
from django.db import transaction


class Command(BaseCommand):
    help = 'Restores a complete backup of the Skinova Clinic system'

    def add_arguments(self, parser):
        parser.add_argument(
            'backup_file',
            type=str,
            help='Path to the backup zip file',
        )
        parser.add_argument(
            '--no-database',
            action='store_true',
            help='Skip database restoration',
        )
        parser.add_argument(
            '--no-media',
            action='store_true',
            help='Skip media files restoration',
        )
        parser.add_argument(
            '--no-static',
            action='store_true',
            help='Skip static files restoration',
        )
        parser.add_argument(
            '--no-data',
            action='store_true',
            help='Skip data import from JSON',
        )

    def handle(self, *args, **options):
        backup_file = Path(options['backup_file'])
        
        if not backup_file.exists():
            raise CommandError(f'Backup file not found: {backup_file}')
        
        self.stdout.write(self.style.WARNING('\n⚠️  RESTORING BACKUP - This will overwrite existing data!'))
        self.stdout.write(self.style.WARNING(f'   Backup file: {backup_file}'))
        
        # Ask for confirmation
        confirm = input('\nAre you sure you want to continue? (yes/no): ')
        if confirm.lower() != 'yes':
            self.stdout.write(self.style.ERROR('Restore cancelled.'))
            return
        
        try:
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                # Read backup info
                if 'BACKUP_INFO.txt' in zipf.namelist():
                    info = zipf.read('BACKUP_INFO.txt').decode('utf-8')
                    self.stdout.write(self.style.SUCCESS('\n📋 Backup Information:'))
                    self.stdout.write(info)
                
                # 1. Restore Database
                if not options['no_database']:
                    self.stdout.write('\n🔄 Restoring database...')
                    db_files = [f for f in zipf.namelist() if f.startswith('database/')]
                    if db_files:
                        db_backup = db_files[0]
                        db_path = Path(settings.DATABASES['default']['NAME'])
                        
                        # Backup current database first
                        if db_path.exists():
                            backup_current = db_path.parent / f'{db_path.name}.backup'
                            shutil.copy2(db_path, backup_current)
                            self.stdout.write(f'   ✓ Current database backed up to {backup_current.name}')
                        
                        # Extract and restore
                        temp_dir = settings.BASE_DIR / 'temp_restore'
                        temp_dir.mkdir(exist_ok=True)
                        zipf.extract(db_backup, temp_dir)
                        extracted_db = temp_dir / db_backup
                        if extracted_db.exists():
                            shutil.move(extracted_db, db_path)
                            self.stdout.write(self.style.SUCCESS(f'   ✓ Database restored from {db_backup}'))
                        # Cleanup
                        if temp_dir.exists():
                            shutil.rmtree(temp_dir)
                    else:
                        self.stdout.write(self.style.WARNING('   ⚠ No database file in backup'))
                
                # 2. Restore Data from JSON
                if not options['no_data']:
                    self.stdout.write('\n📄 Restoring data from JSON...')
                    if 'data_export.json' in zipf.namelist():
                        # Flush existing data first
                        self.stdout.write('   Clearing existing data...')
                        call_command('flush', '--noinput')
                        
                        # Load data
                        json_data = zipf.read('data_export.json')
                        json_file = settings.BASE_DIR / 'temp_restore.json'
                        json_file.write_bytes(json_data)
                        
                        try:
                            call_command('loaddata', str(json_file))
                            self.stdout.write(self.style.SUCCESS('   ✓ Data restored from JSON'))
                        finally:
                            if json_file.exists():
                                json_file.unlink()
                    else:
                        self.stdout.write(self.style.WARNING('   ⚠ No data export file in backup'))
                
                # 3. Restore Media Files
                if not options['no_media']:
                    self.stdout.write('\n🖼️  Restoring media files...')
                    media_files = [f for f in zipf.namelist() if f.startswith('media/')]
                    if media_files:
                        media_root = Path(settings.MEDIA_ROOT)
                        media_root.mkdir(parents=True, exist_ok=True)
                        
                        temp_dir = settings.BASE_DIR / 'temp_restore'
                        temp_dir.mkdir(exist_ok=True)
                        for media_file in media_files:
                            zipf.extract(media_file, temp_dir)
                            extracted = temp_dir / media_file
                            target = media_root / Path(media_file).relative_to('media')
                            target.parent.mkdir(parents=True, exist_ok=True)
                            if extracted.exists():
                                shutil.move(extracted, target)
                        # Cleanup
                        if temp_dir.exists():
                            shutil.rmtree(temp_dir)
                        
                        self.stdout.write(self.style.SUCCESS(f'   ✓ {len(media_files)} media files restored'))
                    else:
                        self.stdout.write(self.style.WARNING('   ⚠ No media files in backup'))
                
                # 4. Restore Static Files
                if not options['no_static']:
                    self.stdout.write('\n🎨 Restoring static files...')
                    static_files = [f for f in zipf.namelist() if f.startswith('static/')]
                    if static_files:
                        static_dir = Path(settings.BASE_DIR) / 'static'
                        static_dir.mkdir(parents=True, exist_ok=True)
                        
                        temp_dir = settings.BASE_DIR / 'temp_restore'
                        temp_dir.mkdir(exist_ok=True)
                        for static_file in static_files:
                            zipf.extract(static_file, temp_dir)
                            extracted = temp_dir / static_file
                            # Reconstruct path
                            parts = Path(static_file).parts[1:]  # Remove 'static/' prefix
                            target = static_dir / Path(*parts)
                            target.parent.mkdir(parents=True, exist_ok=True)
                            if extracted.exists():
                                shutil.move(extracted, target)
                        # Cleanup
                        if temp_dir.exists():
                            shutil.rmtree(temp_dir)
                        
                        self.stdout.write(self.style.SUCCESS(f'   ✓ {len(static_files)} static files restored'))
                    else:
                        self.stdout.write(self.style.WARNING('   ⚠ No static files in backup'))
                
                # 5. Restore Requirements (optional)
                if 'requirements.txt' in zipf.namelist():
                    self.stdout.write('\n📋 Backup includes requirements.txt')
                    self.stdout.write('   Run: pip install -r requirements.txt')
            
            self.stdout.write(self.style.SUCCESS('\n✅ Restore completed successfully!'))
            self.stdout.write(self.style.SUCCESS('   You may need to run: python manage.py collectstatic'))
            self.stdout.write(self.style.SUCCESS('   And: python manage.py migrate'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error restoring backup: {e}'))
            raise

