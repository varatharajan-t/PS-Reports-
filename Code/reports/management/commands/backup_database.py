"""
Management command to backup the database.
Supports SQLite and PostgreSQL databases with automatic cleanup of old backups.
"""
import os
import shutil
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connection
import subprocess


class Command(BaseCommand):
    help = 'Create a backup of the database with automatic cleanup of old backups'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default=None,
            help='Directory to store backups (default: BASE_DIR/backups/database)'
        )
        parser.add_argument(
            '--keep-days',
            type=int,
            default=30,
            help='Number of days to keep backups (default: 30)'
        )
        parser.add_argument(
            '--compress',
            action='store_true',
            help='Compress the backup file with gzip'
        )
        parser.add_argument(
            '--no-cleanup',
            action='store_true',
            help='Skip cleanup of old backups'
        )

    def handle(self, *args, **options):
        # Determine output directory
        output_dir = options['output_dir']
        if not output_dir:
            output_dir = settings.BASE_DIR / 'backups' / 'database'
        else:
            output_dir = Path(output_dir)

        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)

        # Get database configuration
        db_config = settings.DATABASES['default']
        db_engine = db_config['ENGINE']

        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        try:
            if 'sqlite' in db_engine:
                backup_file = self.backup_sqlite(db_config, output_dir, timestamp, options['compress'])
            elif 'postgresql' in db_engine:
                backup_file = self.backup_postgresql(db_config, output_dir, timestamp, options['compress'])
            else:
                raise CommandError(f'Unsupported database engine: {db_engine}')

            self.stdout.write(self.style.SUCCESS(f'✓ Backup created successfully: {backup_file}'))

            # Get file size
            file_size = os.path.getsize(backup_file)
            file_size_mb = file_size / (1024 * 1024)
            self.stdout.write(self.style.SUCCESS(f'  File size: {file_size_mb:.2f} MB'))

            # Cleanup old backups
            if not options['no_cleanup']:
                deleted_count = self.cleanup_old_backups(output_dir, options['keep_days'])
                if deleted_count > 0:
                    self.stdout.write(self.style.WARNING(f'  Cleaned up {deleted_count} old backup(s)'))

        except Exception as e:
            raise CommandError(f'Backup failed: {str(e)}')

    def backup_sqlite(self, db_config, output_dir, timestamp, compress):
        """Backup SQLite database."""
        db_path = db_config['NAME']

        if not os.path.exists(db_path):
            raise CommandError(f'Database file not found: {db_path}')

        # Generate backup filename
        backup_filename = f'backup_{timestamp}.sqlite3'
        if compress:
            backup_filename += '.gz'

        backup_path = output_dir / backup_filename

        self.stdout.write('Backing up SQLite database...')

        if compress:
            # Copy and compress
            with open(db_path, 'rb') as f_in:
                with gzip.open(backup_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            # Simple copy
            shutil.copy2(db_path, backup_path)

        return backup_path

    def backup_postgresql(self, db_config, output_dir, timestamp, compress):
        """Backup PostgreSQL database using pg_dump."""
        db_name = db_config['NAME']
        db_user = db_config.get('USER', 'postgres')
        db_host = db_config.get('HOST', 'localhost')
        db_port = db_config.get('PORT', '5432')
        db_password = db_config.get('PASSWORD', '')

        # Generate backup filename
        backup_filename = f'backup_{timestamp}.sql'
        if compress:
            backup_filename += '.gz'

        backup_path = output_dir / backup_filename

        self.stdout.write('Backing up PostgreSQL database...')

        # Prepare pg_dump command
        cmd = [
            'pg_dump',
            '-h', db_host,
            '-p', str(db_port),
            '-U', db_user,
            '-F', 'c',  # Custom format (compressed)
            '-f', str(backup_path),
            db_name
        ]

        # Set password in environment
        env = os.environ.copy()
        if db_password:
            env['PGPASSWORD'] = db_password

        try:
            subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise CommandError(f'pg_dump failed: {e.stderr}')
        except FileNotFoundError:
            raise CommandError('pg_dump not found. Please install PostgreSQL client tools.')

        return backup_path

    def cleanup_old_backups(self, backup_dir, keep_days):
        """Delete backups older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        deleted_count = 0

        for backup_file in backup_dir.glob('backup_*'):
            # Extract timestamp from filename
            try:
                # Format: backup_YYYYMMDD_HHMMSS.*
                timestamp_str = backup_file.stem.split('_')[1] + backup_file.stem.split('_')[2]
                if '.gz' in backup_file.name:
                    timestamp_str = timestamp_str.replace('.sqlite3', '')

                file_date = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')

                if file_date < cutoff_date:
                    backup_file.unlink()
                    deleted_count += 1
                    self.stdout.write(self.style.WARNING(f'  Deleted old backup: {backup_file.name}'))
            except (ValueError, IndexError):
                # Skip files that don't match expected format
                continue

        return deleted_count
