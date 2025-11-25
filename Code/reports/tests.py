from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
import pandas as pd
from .models import WBSElement
from .services.data_processing import MasterDataManager, WBSProcessor

class ReportPageTests(TestCase):
    """
    Tests for the views of the reports app.
    """
    def test_dashboard_view_status_code(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_view_uses_correct_template(self):
        response = self.client.get(reverse('dashboard'))
        self.assertTemplateUsed(response, 'reports/dashboard.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_budget_report_page_status_code(self):
        response = self.client.get(reverse('report_budget'))
        self.assertEqual(response.status_code, 200)
        
    def test_budget_report_page_uses_correct_template(self):
        response = self.client.get(reverse('report_budget'))
        self.assertTemplateUsed(response, 'reports/report_budget.html')

class ServicesTests(TestCase):
    """
    Tests for the business logic in the service layer.
    """
    @classmethod
    def setUpTestData(cls):
        # Create WBS elements in the test database
        WBSElement.objects.create(wbs_element="PRJ001", name="Project One")
        WBSElement.objects.create(wbs_element="PRJ002", name="Project Two")

    def test_map_wbs_descriptions(self):
        """
        Tests that the MasterDataManager correctly maps descriptions from the database.
        """
        manager = MasterDataManager()
        transaction_data = pd.DataFrame({
            ('WBS_Elements_Info.', 'ID_No'): ["PRJ001", "PRJ003", "PRJ002"],
            ('WBS_Elements_Info.', 'Description'): ["", "", ""]
        })

        result_df = manager.map_wbs_descriptions(
            transaction_df=transaction_data,
            wbs_column=('WBS_Elements_Info.', 'ID_No'),
            description_column=('WBS_Elements_Info.', 'Description')
        )
        
        self.assertEqual(result_df.loc[0, ('WBS_Elements_Info.', 'Description')], "Project One")
        self.assertEqual(result_df.loc[2, ('WBS_Elements_Info.', 'Description')], "Project Two")
        self.assertEqual(result_df.loc[1, ('WBS_Elements_Info.', 'Description')], "") # Not found

class FileUploadTests(TestCase):
    """
    Tests for the file upload functionality.
    """
    @patch('reports.views.generate_budget_report')
    def test_budget_report_upload(self, mock_generate_report):
        """
        Tests the file upload process for the budget report view.
        """
        # Configure the mock to return a dictionary with expected keys
        mock_generate_report.return_value = {
            "file_path": "/fake/path/report.xlsx",
            "data_html": "<table></table>"
        }

        # Create a dummy file for upload
        dummy_file_content = b"header\ndata"
        dummy_file = SimpleUploadedFile("test.dat", dummy_file_content, content_type="text/plain")

        response = self.client.post(reverse('report_budget'), {'file': dummy_file})

        # Check that the view responds correctly
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/report_budget.html')
        
        # Check that the service was called with the uploaded file path
        mock_generate_report.assert_called_once()
        
        # Check that the context contains the results from the service
        self.assertIn('report_file_name', response.context)
        self.assertIn('data_html', response.context)
        self.assertEqual(response.context['report_file_name'], 'report.xlsx')
        self.assertEqual(response.context['data_html'], '<table></table>')