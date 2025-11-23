"""
Management command to create a superuser from environment variables
Run with: python manage.py create_superuser
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates a superuser from environment variables (SUPERUSER_USERNAME, SUPERUSER_PASSWORD, SUPERUSER_EMAIL)'

    def handle(self, *args, **options):
        username = os.environ.get('SUPERUSER_USERNAME', 'admin')
        password = os.environ.get('SUPERUSER_PASSWORD')
        email = os.environ.get('SUPERUSER_EMAIL', '')

        if not password:
            self.stdout.write(
                self.style.ERROR(
                    'SUPERUSER_PASSWORD environment variable is required!\n'
                    'Set it in Render: Environment → Add Environment Variable'
                )
            )
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Superuser "{username}" already exists. Skipping.')
            )
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            role='ADMIN'
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Superuser "{username}" created successfully!\n'
                f'You can now log in at /admin/'
            )
        )

