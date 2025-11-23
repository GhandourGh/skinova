# Skinova Clinic - POS & Booking System

A full-stack Django application for managing appointments and point of sale operations for a skincare clinic.

## Quick Start

### 1. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 2. Create Superuser (First Time Only)
```bash
python manage.py createsuperuser
```
Follow the prompts to create an admin account.

### 3. Run Development Server
```bash
python manage.py runserver
```

### 4. Access the Application
- Home: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

## Project Structure

- **core**: User authentication and custom user model (Admin, Doctor, Receptionist, Patient roles)
- **appointments**: Service booking system with double-booking prevention
- **pos**: Point of sale system for products and services
- **inventory**: Inventory dashboard with low-stock alerts

## Database

Currently using SQLite (db.sqlite3) for development. Compatible with PostgreSQL for production.

## Backup & Restore System

### Create Backup
```bash
python manage.py backup_system
```
Creates a complete backup in `backups/` folder including:
- Database (SQLite)
- All data (JSON export)
- Media files (images, uploads)
- Static files (logos, custom CSS)
- Requirements file

### Restore Backup
```bash
python manage.py restore_system backups/skinova_backup_YYYY-MM-DD_HH-MM-SS.zip
```
Restores all data, files, and database from backup.

### Web Interface
Access backup management at: `/backup/` or click "Backup" in admin top menu.

## Next Steps

1. Create a superuser account to access Django admin
2. Add Services, Products, and Staff Members through admin
3. Book appointments and process POS transactions
4. Create regular backups before system changes or migrations

