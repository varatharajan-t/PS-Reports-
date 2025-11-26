"""
Context processors for adding global template variables.
"""
from pathlib import Path
from django.conf import settings
from .models import WBSElement


def wbs_data_status(request):
    """
    Add WBS master data status to all template contexts.
    Shows a warning if WBS data is not loaded.
    """
    wbs_count = WBSElement.objects.count()
    wbs_available = wbs_count > 0

    context = {
        'wbs_data_available': wbs_available,
        'wbs_element_count': wbs_count,
    }

    if not wbs_available:
        wbs_file_path = Path(settings.MASTER_WBS_FILE)

        if wbs_file_path.exists():
            context['wbs_warning'] = {
                'type': 'warning',
                'message': (
                    'WBS master data not loaded. '
                    f'File found at {wbs_file_path.name}. '
                    'Run <code>python manage.py import_master_data</code> to import it.'
                ),
                'action': 'Import master data',
            }
        else:
            context['wbs_warning'] = {
                'type': 'danger',
                'message': (
                    f'WBS master data file (WBS_NAMES.XLSX) not found in data/ directory. '
                    'Please place the file and run <code>python manage.py import_master_data</code>.'
                ),
                'action': 'Add WBS_NAMES.XLSX file',
            }

    return context


def system_status(request):
    """
    Add overall system status information to all template contexts.
    """
    from .models import CompanyCode, ProjectType

    return {
        'system_stats': {
            'company_codes': CompanyCode.objects.count(),
            'project_types': ProjectType.objects.count(),
            'wbs_elements': WBSElement.objects.count(),
        }
    }
