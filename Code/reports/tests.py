"""
Legacy tests file - now using the tests/ directory structure.

All tests have been moved to the reports/tests/ directory:
- test_models.py - Database model tests
- test_views.py - View tests
- test_forms.py - Form validation tests
- test_formatting.py - Formatting function tests
- test_data_processing.py - Data processing tests
- test_context_processors.py - Context processor tests
- test_commands.py - Management command tests

Run tests with: python manage.py test
"""

# Import all tests from the new test directory
from .tests.test_models import *
from .tests.test_views import *
from .tests.test_forms import *
from .tests.test_formatting import *
from .tests.test_data_processing import *
from .tests.test_context_processors import *
from .tests.test_commands import *