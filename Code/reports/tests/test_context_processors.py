"""
Tests for context processors.
"""
from django.test import TestCase, RequestFactory
from unittest.mock import patch, MagicMock
from pathlib import Path
from reports.context_processors import wbs_data_status, system_status
from reports.models import WBSElement, CompanyCode, ProjectType


class WBSDataStatusContextProcessorTest(TestCase):
    """Tests for wbs_data_status context processor."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.request = self.factory.get('/')

    def test_wbs_data_available(self):
        """Test context when WBS data is available."""
        # Create WBS elements
        WBSElement.objects.create(wbs_element="P-001", name="Project One")
        WBSElement.objects.create(wbs_element="P-002", name="Project Two")

        context = wbs_data_status(self.request)

        self.assertTrue(context['wbs_data_available'])
        self.assertEqual(context['wbs_element_count'], 2)
        self.assertNotIn('wbs_warning', context)

    def test_wbs_data_not_available_file_exists(self):
        """Test context when WBS data not loaded but file exists."""
        # Ensure no WBS elements
        WBSElement.objects.all().delete()

        # Mock file existence
        with patch('pathlib.Path.exists', return_value=True):
            context = wbs_data_status(self.request)

            self.assertFalse(context['wbs_data_available'])
            self.assertEqual(context['wbs_element_count'], 0)
            self.assertIn('wbs_warning', context)
            self.assertEqual(context['wbs_warning']['type'], 'warning')
            self.assertIn('import_master_data', context['wbs_warning']['message'])

    def test_wbs_data_not_available_file_missing(self):
        """Test context when WBS data not loaded and file missing."""
        # Ensure no WBS elements
        WBSElement.objects.all().delete()

        # Mock file not existing
        with patch('pathlib.Path.exists', return_value=False):
            context = wbs_data_status(self.request)

            self.assertFalse(context['wbs_data_available'])
            self.assertIn('wbs_warning', context)
            self.assertEqual(context['wbs_warning']['type'], 'danger')
            self.assertIn('WBS_NAMES.XLSX', context['wbs_warning']['message'])

    def test_wbs_warning_message_format(self):
        """Test that warning messages are properly formatted."""
        WBSElement.objects.all().delete()

        with patch('pathlib.Path.exists', return_value=True):
            context = wbs_data_status(self.request)

            # Should contain HTML <code> tags for commands
            self.assertIn('<code>', context['wbs_warning']['message'])
            self.assertIn('</code>', context['wbs_warning']['message'])

    def test_wbs_context_keys(self):
        """Test that all expected keys are in the context."""
        WBSElement.objects.create(wbs_element="P-001", name="Project")

        context = wbs_data_status(self.request)

        required_keys = ['wbs_data_available', 'wbs_element_count']
        for key in required_keys:
            self.assertIn(key, context)


class SystemStatusContextProcessorTest(TestCase):
    """Tests for system_status context processor."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.request = self.factory.get('/')

        # Create test data
        CompanyCode.objects.create(code="1000", name="Company A")
        CompanyCode.objects.create(code="2000", name="Company B")

        ProjectType.objects.create(code="CAP", name="Capital")
        ProjectType.objects.create(code="OM", name="O&M")

        WBSElement.objects.create(wbs_element="P-001", name="Project One")

    def test_system_status_structure(self):
        """Test that system_status returns correct structure."""
        context = system_status(self.request)

        self.assertIn('system_stats', context)
        self.assertIsInstance(context['system_stats'], dict)

    def test_system_status_counts(self):
        """Test that system_status returns correct counts."""
        context = system_status(self.request)

        stats = context['system_stats']
        self.assertEqual(stats['company_codes'], 2)
        self.assertEqual(stats['project_types'], 2)
        self.assertEqual(stats['wbs_elements'], 1)

    def test_system_status_with_empty_database(self):
        """Test system_status when database is empty."""
        # Clear all data
        CompanyCode.objects.all().delete()
        ProjectType.objects.all().delete()
        WBSElement.objects.all().delete()

        context = system_status(self.request)

        stats = context['system_stats']
        self.assertEqual(stats['company_codes'], 0)
        self.assertEqual(stats['project_types'], 0)
        self.assertEqual(stats['wbs_elements'], 0)

    def test_system_status_keys(self):
        """Test that all expected keys are present."""
        context = system_status(self.request)

        required_keys = ['company_codes', 'project_types', 'wbs_elements']
        for key in required_keys:
            self.assertIn(key, context['system_stats'])


class CombinedContextProcessorsTest(TestCase):
    """Tests for combined usage of context processors."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.request = self.factory.get('/')

    def test_both_processors_work_together(self):
        """Test that both context processors can be used together."""
        # Create test data
        WBSElement.objects.create(wbs_element="P-001", name="Project")
        CompanyCode.objects.create(code="1000", name="Company")

        wbs_context = wbs_data_status(self.request)
        system_context = system_status(self.request)

        # Both should return valid contexts
        self.assertIsInstance(wbs_context, dict)
        self.assertIsInstance(system_context, dict)

        # No key conflicts
        all_keys = set(wbs_context.keys()) | set(system_context.keys())
        self.assertEqual(
            len(all_keys),
            len(wbs_context.keys()) + len(system_context.keys())
        )

    def test_context_processors_with_different_request_types(self):
        """Test context processors with GET and POST requests."""
        get_request = self.factory.get('/some-url/')
        post_request = self.factory.post('/some-url/')

        WBSElement.objects.create(wbs_element="P-001", name="Project")

        # Both request types should work
        get_context = wbs_data_status(get_request)
        post_context = wbs_data_status(post_request)

        self.assertEqual(get_context, post_context)
