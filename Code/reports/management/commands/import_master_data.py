import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from reports.models import CompanyCode, ProjectType, WBSElement

class Command(BaseCommand):
    help = 'Imports master data from settings and the WBS_NAMES.XLSX file into the database.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting master data import...'))

        # --- 1. Import Company Codes ---
        self.stdout.write('Deleting existing Company Codes...')
        CompanyCode.objects.all().delete()
        
        self.stdout.write('Importing Company Codes from settings...')
        company_codes_data = settings.COMPANY_CODES
        codes_created = 0
        for code, name in company_codes_data.items():
            _, created = CompanyCode.objects.get_or_create(code=code, defaults={'name': name})
            if created:
                codes_created += 1
        self.stdout.write(self.style.SUCCESS(f'Successfully created {codes_created} new Company Codes.'))

        # --- 2. Import Project Types ---
        self.stdout.write('\nDeleting existing Project Types...')
        ProjectType.objects.all().delete()

        self.stdout.write('Importing Project Types from settings...')
        project_types_data = settings.PROJECT_TYPES
        types_created = 0
        for code, name in project_types_data.items():
            _, created = ProjectType.objects.get_or_create(code=code, defaults={'name': name})
            if created:
                types_created += 1
        self.stdout.write(self.style.SUCCESS(f'Successfully created {types_created} new Project Types.'))

        # --- 3. Import WBS Elements ---
        wbs_file_path = settings.MASTER_WBS_FILE
        self.stdout.write(f'\nAttempting to read WBS data from: {wbs_file_path}')
        
        try:
            # Check if file exists before trying to read
            if not wbs_file_path.exists():
                self.stdout.write(self.style.ERROR(f'Error: Master WBS file not found at {wbs_file_path}'))
                self.stdout.write(self.style.WARNING('Please ensure the WBS_NAMES.XLSX file is in the "data" directory at the project root.'))
                # The transaction will be rolled back, so no partial data will be committed.
                raise FileNotFoundError(f"File not found: {wbs_file_path}")

            self.stdout.write('Deleting existing WBS Elements...')
            WBSElement.objects.all().delete()
            
            self.stdout.write('Reading WBS Elements from Excel file...')
            df = pd.read_excel(wbs_file_path)

            # Validate required columns
            if 'WBS_element' not in df.columns or 'Name' not in df.columns:
                self.stdout.write(self.style.ERROR('Excel file must contain "WBS_element" and "Name" columns.'))
                raise ValueError("Missing required columns in Excel file.")

            wbs_elements_to_create = []
            for index, row in df.iterrows():
                wbs_code = str(row['WBS_element']).strip()
                wbs_name = str(row['Name']).strip()
                if wbs_code and wbs_name: # Ensure we don't import empty rows
                    wbs_elements_to_create.append(
                        WBSElement(wbs_element=wbs_code, name=wbs_name)
                    )
            
            WBSElement.objects.bulk_create(wbs_elements_to_create)
            self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(wbs_elements_to_create)} WBS Elements.'))

        except FileNotFoundError as e:
            # Error already printed, just ensuring the command exits non-zero
            # The transaction will handle the rollback.
            raise e
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An unexpected error occurred during WBS import: {e}'))
            # The transaction will be rolled back.
            raise e

        self.stdout.write(self.style.SUCCESS('\nMaster data import completed successfully!'))
