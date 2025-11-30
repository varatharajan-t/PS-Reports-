"""
Management command to restore the database from a backup.
Supports SQLite and PostgreSQL databases.
"""
import os
import shutil
import gzip
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import subprocess


class Command(BaseCommand):
    help = 'Restore the database from a backup file'

    def add_arguments(self, parser):
        parser.add_argument(
            'backup_file',
            type=str,
            help='Path to the backup file to restore'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force restore without confirmation prompt'
        )

    def handle(self, *args, **options):
        backup_file = Path(options['backup_file'])

        if not backup_file.exists():
            raise CommandError(f'Backup file not found: {backup_file}')

        # Get database configuration
        db_config = settings.DATABASES['default']
        db_engine = db_config['ENGINE']

        # Confirm restore (unless forced)
        if not options['force']:
            self.stdout.write(self.style.WARNING('⚠ WARNING: This will replace the current database!'))
            self.stdout.write(f'Backup file: {backup_file}')
            confirm = input('Are you sure you want to continue? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('Restore cancelled.'))
                return

        try:
            if 'sqlite' in db_engine:
                self.restore_sqlite(db_config, backup_file)
            elif 'postgresql' in db_engine:
                self.restore_postgresql(db_config, backup_file)
            else:
                raise CommandError(f'Unsupported database engine: {db_engine}')

            self.stdout.write(self.style.SUCCESS(f'✓ Database restored successfully from: {backup_file}'))

        except Exception as e:
            raise CommandError(f'Restore failed: {str(e)}')

    def restore_sqlite(self, db_config, backup_file):
        """Restore SQLite database."""
        db_path = Path(db_config['NAME'])

        self.stdout.write('Restoring SQLite database...')

        # Create backup of current database before restoring
        if db_path.exists():
            backup_current = db_path.with_suffix('.sqlite3.before_restore')
            shutil.copy2(db_path, backup_current)
            self.stdout.write(f'  Current database backed up to: {backup_current}')

        # Restore from backup
        if backup_file.suffix == '.gz':
            # Decompress and restore
            with gzip.open(backup_file, 'rb') as f_in:
                with open(db_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            # Simple copy
            shutil.copy2(backup_file, db_path)

    def restore_postgresql(self, db_config, backup_file):
        """Restore PostgreSQL database using pg_restore."""
        db_name = db_config['NAME']
        db_user = db_config.get('USER', 'postgres')
        db_host = db_config.get('HOST', 'localhost')
        db_port = db_config.get('PORT', '5432')
        db_password = db_config.get('PASSWORD', '')

        self.stdout.write('Restoring PostgreSQL database...')

        # Prepare pg_restore command
        cmd = [
            'pg_restore',
            '-h', db_host,
            '-p', str(db_port),
            '-U', db_user,
            '-d', db_name,
            '--clean',  # Drop existing objects before restoring
            '--if-exists',  # Don't error if objects don't exist
            str(backup_file)
        ]

        # Set password in environment
        env = os.environ.copy()
        if db_password:
            env['PGPASSWORD'] = db_password

        try:
            subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise CommandError(f'pg_restore failed: {e.stderr}')
        except FileNotFoundError:
            raise CommandError('pg_restore not found. Please install PostgreSQL client tools.')
