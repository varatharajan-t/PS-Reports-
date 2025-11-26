"""
Management command to check WBS master data status.
"""
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from reports.models import WBSElement, CompanyCode, ProjectType


class Command(BaseCommand):
    help = 'Checks the status of WBS master data and provides recommendations.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('WBS Master Data Status Check'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        # Check WBS file
        wbs_file_path = Path(settings.MASTER_WBS_FILE)
        self.stdout.write(f'\n📁 WBS File Location: {wbs_file_path}')

        if wbs_file_path.exists():
            file_size = wbs_file_path.stat().st_size / 1024  # KB
            self.stdout.write(self.style.SUCCESS(f'   ✓ File exists ({file_size:.2f} KB)'))
        else:
            self.stdout.write(self.style.ERROR(f'   ✗ File not found!'))
            self.stdout.write(self.style.WARNING(
                f'   → Place WBS_NAMES.XLSX in the data/ directory at: {wbs_file_path.parent}'
            ))

        # Check database records
        self.stdout.write('\n📊 Database Status:')

        # WBS Elements
        wbs_count = WBSElement.objects.count()
        if wbs_count > 0:
            self.stdout.write(self.style.SUCCESS(f'   ✓ WBS Elements: {wbs_count} records'))

            # Show sample WBS elements
            sample_wbs = WBSElement.objects.all()[:5]
            if sample_wbs:
                self.stdout.write('   Sample WBS Elements:')
                for wbs in sample_wbs:
                    self.stdout.write(f'      • {wbs.wbs_element}: {wbs.name}')
        else:
            self.stdout.write(self.style.ERROR(f'   ✗ WBS Elements: 0 records (not loaded)'))

        # Company Codes
        cc_count = CompanyCode.objects.count()
        if cc_count > 0:
            self.stdout.write(self.style.SUCCESS(f'   ✓ Company Codes: {cc_count} records'))
        else:
            self.stdout.write(self.style.WARNING(f'   ⚠ Company Codes: 0 records'))

        # Project Types
        pt_count = ProjectType.objects.count()
        if pt_count > 0:
            self.stdout.write(self.style.SUCCESS(f'   ✓ Project Types: {pt_count} records'))
        else:
            self.stdout.write(self.style.WARNING(f'   ⚠ Project Types: 0 records'))

        # Recommendations
        self.stdout.write('\n💡 Recommendations:')

        if wbs_count == 0:
            if wbs_file_path.exists():
                self.stdout.write(self.style.WARNING(
                    '   → Run: python manage.py import_master_data'
                ))
                self.stdout.write('      This will import WBS data from the file into the database.')
            else:
                self.stdout.write(self.style.ERROR(
                    '   → First, add WBS_NAMES.XLSX to the data/ directory'
                ))
                self.stdout.write(self.style.WARNING(
                    '   → Then run: python manage.py import_master_data'
                ))
        elif wbs_count < 100:
            self.stdout.write(self.style.WARNING(
                f'   ⚠ Only {wbs_count} WBS elements loaded. This seems low.'
            ))
            self.stdout.write('      Ensure the WBS_NAMES.XLSX file contains all required elements.')
        else:
            self.stdout.write(self.style.SUCCESS(
                '   ✓ WBS master data looks good!'
            ))
            self.stdout.write('      Reports will include WBS descriptions.')

        if cc_count == 0 or pt_count == 0:
            self.stdout.write(self.style.WARNING(
                '   → Run: python manage.py import_master_data'
            ))
            self.stdout.write('      This will also import Company Codes and Project Types.')

        # Impact on reports
        self.stdout.write('\n📈 Impact on Reports:')
        if wbs_count > 0:
            self.stdout.write(self.style.SUCCESS(
                '   ✓ Reports will show WBS element descriptions'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                '   ⚠ Reports will only show WBS codes (no descriptions)'
            ))
            self.stdout.write('      Reports will still work but with less detail.')

        self.stdout.write('\n' + '=' * 70)

        # Return exit code
        if wbs_count == 0 and not wbs_file_path.exists():
            self.stdout.write(self.style.ERROR(
                '❌ CRITICAL: WBS file not found and database empty!'
            ))
            return  # Exit with error (non-zero)
        elif wbs_count == 0:
            self.stdout.write(self.style.WARNING(
                '⚠ WARNING: WBS data not imported yet.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                '✅ SUCCESS: WBS master data is ready!'
            ))
