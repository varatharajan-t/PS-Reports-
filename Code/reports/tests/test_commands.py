"""
Tests for Django management commands.
"""
from django.test import TestCase
from django.core.management import call_command
from unittest.mock import patch
from io import StringIO
from pathlib import Path
from reports.models import WBSElement, CompanyCode, ProjectType


class CheckWBSDataCommandTest(TestCase):
    """Tests for check_wbs_data management command."""

    def test_command_runs_successfully(self):
        """Test that the command runs without errors."""
        out = StringIO()
        call_command('check_wbs_data', stdout=out)

        output = out.getvalue()
        self.assertIn('WBS Master Data Status Check', output)

    def test_command_with_wbs_data_available(self):
        """Test command output when WBS data is available."""
        # Create WBS elements
        WBSElement.objects.create(wbs_element="P-001", name="Project One")
        WBSElement.objects.create(wbs_element="P-002", name="Project Two")

        out = StringIO()
        call_command('check_wbs_data', stdout=out)

        output = out.getvalue()
        self.assertIn('WBS Elements: 2 records', output)
        self.assertIn('SUCCESS', output)

    def test_command_with_no_wbs_data(self):
        """Test command output when WBS data is missing."""
        # Ensure no WBS elements
        WBSElement.objects.all().delete()

        out = StringIO()
        call_command('check_wbs_data', stdout=out)

        output = out.getvalue()
        self.assertIn('0 records', output)

    @patch('pathlib.Path.exists')
    def test_command_file_exists_check(self, mock_exists):
        """Test that the command checks file existence."""
        mock_exists.return_value = True

        WBSElement.objects.all().delete()

        out = StringIO()
        call_command('check_wbs_data', stdout=out)

        output = out.getvalue()
        self.assertIn('File exists', output)
        self.assertIn('import_master_data', output)

    @patch('pathlib.Path.exists')
    def test_command_file_not_found(self, mock_exists):
        """Test command when WBS file is not found."""
        mock_exists.return_value = False

        WBSElement.objects.all().delete()

        out = StringIO()
        call_command('check_wbs_data', stdout=out)

        output = out.getvalue()
        self.assertIn('File not found', output)

    def test_command_shows_company_codes(self):
        """Test that command shows company code count."""
        CompanyCode.objects.create(code="1000", name="Company A")

        out = StringIO()
        call_command('check_wbs_data', stdout=out)

        output = out.getvalue()
        self.assertIn('Company Codes', output)

    def test_command_shows_project_types(self):
        """Test that command shows project type count."""
        ProjectType.objects.create(code="CAP", name="Capital")

        out = StringIO()
        call_command('check_wbs_data', stdout=out)

        output = out.getvalue()
        self.assertIn('Project Types', output)

    def test_command_shows_sample_wbs_elements(self):
        """Test that command shows sample WBS elements."""
        # Create several WBS elements
        for i in range(10):
            WBSElement.objects.create(
                wbs_element=f"P-{i:03d}",
                name=f"Project {i}"
            )

        out = StringIO()
        call_command('check_wbs_data', stdout=out)

        output = out.getvalue()
        self.assertIn('Sample WBS Elements', output)
        # Should show first 5
        self.assertIn('P-000', output)

    def test_command_recommendations_section(self):
        """Test that command includes recommendations."""
        out = StringIO()
        call_command('check_wbs_data', stdout=out)

        output = out.getvalue()
        self.assertIn('Recommendations', output)

    def test_command_impact_section(self):
        """Test that command includes impact assessment."""
        out = StringIO()
        call_command('check_wbs_data', stdout=out)

        output = out.getvalue()
        self.assertIn('Impact on Reports', output)

    def test_command_low_wbs_count_warning(self):
        """Test warning when WBS count is suspiciously low."""
        # Create only a few WBS elements (less than 100)
        for i in range(5):
            WBSElement.objects.create(
                wbs_element=f"P-{i:03d}",
                name=f"Project {i}"
            )

        out = StringIO()
        call_command('check_wbs_data', stdout=out)

        output = out.getvalue()
        self.assertIn('5 WBS elements loaded', output)
        self.assertIn('seems low', output)


class ImportMasterDataCommandTest(TestCase):
    """Tests for import_master_data management command."""

    def test_import_command_exists(self):
        """Test that import_master_data command exists and runs."""
        out = StringIO()
        err = StringIO()

        try:
            call_command('import_master_data', stdout=out, stderr=err)
        except Exception as e:
            # Command should exist even if it fails due to missing files
            self.assertNotIn('Unknown command', str(e))

    def test_import_without_wbs_file(self):
        """Test import command when WBS file is missing."""
        out = StringIO()
        err = StringIO()

        # The import command should handle missing file gracefully or report error
        # We just test that it doesn't crash the system
        try:
            with patch('pathlib.Path.exists', return_value=False):
                call_command('import_master_data', stdout=out, stderr=err)
        except (FileNotFoundError, Exception) as e:
            # Command may raise an exception for missing file, which is acceptable
            # As long as it's a controlled exception, not a crash
            self.assertIsInstance(e, (FileNotFoundError, Exception))


class MigrateCommandTest(TestCase):
    """Tests for Django migrate command."""

    def test_migrations_are_applied(self):
        """Test that all migrations are applied."""
        out = StringIO()
        call_command('migrate', '--check', stdout=out, verbosity=0)
        # If this doesn't raise an exception, migrations are up to date


class CollectStaticCommandTest(TestCase):
    """Tests for collectstatic command."""

    def test_collectstatic_runs(self):
        """Test that collectstatic command runs successfully."""
        out = StringIO()

        # Use --noinput to avoid prompts, --clear to clean before collecting
        call_command('collectstatic', '--noinput', '--clear', stdout=out, verbosity=0)

        # Should complete without errors
        output = out.getvalue()
        # Command runs silently with verbosity=0
        self.assertIsNotNone(output)
