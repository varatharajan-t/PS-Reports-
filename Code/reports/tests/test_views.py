"""
Tests for views.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
import tempfile
import os


class DashboardViewTest(TestCase):
    """Tests for dashboard view."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()

    def test_dashboard_status_code(self):
        """Test that dashboard loads successfully."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_uses_correct_template(self):
        """Test that dashboard uses the correct template."""
        response = self.client.get(reverse('dashboard'))
        self.assertTemplateUsed(response, 'reports/dashboard.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_dashboard_context(self):
        """Test that dashboard provides expected context."""
        response = self.client.get(reverse('dashboard'))
        self.assertIn('page_title', response.context)


class BudgetReportViewTest(TestCase):
    """Tests for budget report view."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.url = reverse('report_budget')

    def test_budget_report_get_status_code(self):
        """Test GET request to budget report page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_budget_report_uses_correct_template(self):
        """Test that budget report uses correct template."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'reports/report_budget.html')

    @patch('reports.views.generate_budget_report')
    def test_budget_report_post_with_valid_file(self, mock_generate):
        """Test POST request with valid file upload."""
        # Mock the report generation
        mock_generate.return_value = {
            'file_path': '/tmp/test_report.xlsx',
            'data_html': '<table>Test Data</table>',
            'rows_processed': 100
        }

        # Create a test file
        test_file = SimpleUploadedFile(
            "test.dat",
            b"header\ndata",
            content_type="text/plain"
        )

        response = self.client.post(self.url, {'file': test_file})

        self.assertEqual(response.status_code, 200)
        mock_generate.assert_called_once()

    def test_budget_report_post_without_file(self):
        """Test POST request without file."""
        response = self.client.post(self.url, {})

        # Should show form errors or re-render the page
        self.assertEqual(response.status_code, 200)
        # Check that form exists in context and has errors
        if 'form' in response.context:
            self.assertFalse(response.context['form'].is_valid())

    @patch('reports.views.generate_budget_report')
    def test_budget_report_post_handles_service_error(self, mock_generate):
        """Test POST request when service raises an error."""
        # Mock service to raise an exception
        mock_generate.side_effect = Exception("Test error")

        test_file = SimpleUploadedFile("test.dat", b"data")
        response = self.client.post(self.url, {'file': test_file})

        # Should handle error gracefully
        self.assertEqual(response.status_code, 200)


class BudgetUpdatesViewTest(TestCase):
    """Tests for budget updates report view."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.url = reverse('report_budget_updates')

    def test_budget_updates_get_status_code(self):
        """Test GET request to budget updates page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_budget_updates_uses_correct_template(self):
        """Test correct template usage."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'reports/report_budget_updates.html')


class ProjectTypeWiseViewTest(TestCase):
    """Tests for project type wise report view."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.url = reverse('report_project_type_wise')

    def test_project_type_wise_get_status_code(self):
        """Test GET request to project type wise page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_project_type_wise_uses_correct_template(self):
        """Test correct template usage."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'reports/report_project_type_wise.html')

    @patch('reports.views.generate_project_type_wise_report')
    def test_project_type_wise_excel_upload(self, mock_generate):
        """Test uploading Excel file for project type wise report."""
        mock_generate.return_value = {
            'file_path': '/tmp/report.xlsx',
            'rows_processed': 50
        }

        # Create a mock Excel file
        test_file = SimpleUploadedFile(
            "test.xlsx",
            b"PK\x03\x04",  # Minimal Excel signature
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        response = self.client.post(self.url, {'file': test_file})

        self.assertEqual(response.status_code, 200)
        mock_generate.assert_called_once()


class PlanVarianceViewTest(TestCase):
    """Tests for plan variance report view."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.url = reverse('report_plan_variance')

    def test_plan_variance_get_status_code(self):
        """Test GET request to plan variance page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    @patch('reports.views.generate_plan_variance_report')
    def test_plan_variance_post_with_file(self, mock_generate):
        """Test POST request with file upload."""
        mock_generate.return_value = {
            'file_path': '/tmp/variance.xlsx',
            'summary': {'total': 100, 'variance': 10}
        }

        test_file = SimpleUploadedFile("plan.dat", b"data")
        response = self.client.post(self.url, {'file': test_file})

        self.assertEqual(response.status_code, 200)


class BudgetVarianceViewTest(TestCase):
    """Tests for budget variance report view."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.url = reverse('report_budget_variance')

    def test_budget_variance_get_status_code(self):
        """Test GET request to budget variance page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class GlimpsOfProjectsViewTest(TestCase):
    """Tests for glimps of projects view."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.url = reverse('report_glimps_of_projects')

    def test_glimps_of_projects_get_status_code(self):
        """Test GET request to glimps of projects page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    @patch('reports.views.generate_glimps_of_projects_report')
    def test_glimps_of_projects_post(self, mock_generate):
        """Test POST request for glimps of projects."""
        mock_generate.return_value = {
            'file_path': '/tmp/glimps.xlsx',
            'charts_created': 4
        }

        test_file = SimpleUploadedFile("data.dat", b"test data")
        response = self.client.post(self.url, {'file': test_file})

        self.assertEqual(response.status_code, 200)


class ProjectAnalysisViewTest(TestCase):
    """Tests for project analysis report view."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.url = reverse('report_project_analysis')

    def test_project_analysis_get_status_code(self):
        """Test GET request to project analysis page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_project_analysis_uses_correct_template(self):
        """Test correct template usage."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'reports/report_project_analysis.html')

    @patch('reports.views.generate_project_analysis_report')
    def test_project_analysis_two_file_upload(self, mock_generate):
        """Test uploading two files for project analysis."""
        mock_generate.return_value = {
            'file_path': '/tmp/analysis.xlsx',
            'budget_projects': 50,
            'actual_projects': 45,
            'rows_processed': 95
        }

        budget_file = SimpleUploadedFile("budget.dat", b"budget data")
        plan_file = SimpleUploadedFile("plan.dat", b"plan data")

        response = self.client.post(self.url, {
            'budget_file': budget_file,
            'plan_file': plan_file
        })

        self.assertEqual(response.status_code, 200)
        mock_generate.assert_called_once()

    def test_project_analysis_missing_budget_file(self):
        """Test POST with only one file."""
        plan_file = SimpleUploadedFile("plan.dat", b"plan data")

        response = self.client.post(self.url, {'plan_file': plan_file})

        # Should show form errors
        self.assertEqual(response.status_code, 200)


class FileDownloadTest(TestCase):
    """Tests for file download functionality."""

    def setUp(self):
        """Set up test client and temporary file."""
        self.client = Client()
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test_report.xlsx')

        # Create a test file
        with open(self.test_file, 'wb') as f:
            f.write(b"Test Excel content")

    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        os.rmdir(self.temp_dir)

    @patch('reports.views.generate_budget_report')
    def test_download_response_headers(self, mock_generate):
        """Test that download responses have correct headers."""
        mock_generate.return_value = {
            'file_path': self.test_file,
            'data_html': '<table></table>'
        }

        test_file = SimpleUploadedFile("test.dat", b"data")
        response = self.client.post(reverse('report_budget'), {'file': test_file})

        # Context should have download information
        self.assertIn('report_file_name', response.context)


class ErrorHandlingTest(TestCase):
    """Tests for error handling in views."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()

    @patch('reports.views.generate_budget_report')
    def test_service_exception_handling(self, mock_generate):
        """Test that service exceptions are handled gracefully."""
        # Mock service to raise various exceptions
        exceptions_to_test = [
            ValueError("Invalid data"),
            FileNotFoundError("File not found"),
            Exception("Generic error")
        ]

        for exception in exceptions_to_test:
            mock_generate.side_effect = exception

            test_file = SimpleUploadedFile("test.dat", b"data")
            response = self.client.post(reverse('report_budget'), {'file': test_file})

            # Should not crash
            self.assertEqual(response.status_code, 200)

    def test_invalid_url(self):
        """Test accessing invalid URL."""
        response = self.client.get('/invalid-url/')
        self.assertEqual(response.status_code, 404)
