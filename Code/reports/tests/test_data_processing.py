"""
Tests for data processing services.
"""
from django.test import TestCase
from django.conf import settings
import pandas as pd
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from reports.services.data_processing import (
    BaseDataProcessor,
    MasterDataManager,
    WBSProcessor
)
from reports.models import WBSElement, CompanyCode, ProjectType


class ConcreteDataProcessor(BaseDataProcessor):
    """Concrete implementation of BaseDataProcessor for testing."""

    def validate_input(self, file_path: str) -> bool:
        """Validate input file format and content."""
        return Path(file_path).exists()

    def process_data(self, file_path: str) -> pd.DataFrame:
        """Process the input data and return cleaned DataFrame."""
        return self.read_dat_file(file_path, delimiter='\t', header_rows=[0])


class BaseDataProcessorTest(TestCase):
    """Tests for BaseDataProcessor class."""

    def setUp(self):
        """Set up test data."""
        self.processor = ConcreteDataProcessor(module_name="test_processor")
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test files."""
        for file in Path(self.temp_dir).glob('*'):
            file.unlink()
        os.rmdir(self.temp_dir)

    def test_read_dat_file_with_single_header(self):
        """Test reading a DAT file with single header row."""
        # Create a test DAT file
        test_file = os.path.join(self.temp_dir, 'test.dat')
        content = "Col1\tCol2\tCol3\nVal1\tVal2\tVal3\nVal4\tVal5\tVal6"

        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)

        df = self.processor.read_dat_file(test_file, delimiter='\t', header_rows=[0])

        self.assertEqual(df.shape[0], 2)  # 2 data rows
        self.assertEqual(df.shape[1], 3)  # 3 columns

    def test_validate_input(self):
        """Test input validation."""
        # Create a test file
        test_file = os.path.join(self.temp_dir, 'test.dat')
        with open(test_file, 'w') as f:
            f.write("test")

        # Should validate existing file
        result = self.processor.validate_input(test_file)
        self.assertTrue(result)

        # Should not validate non-existing file
        result = self.processor.validate_input('/nonexistent/file.dat')
        self.assertFalse(result)

    def test_clean_dat_file(self):
        """Test cleaning DAT files."""
        input_file = os.path.join(self.temp_dir, 'input.dat')
        output_file = os.path.join(self.temp_dir, 'output.dat')

        # Create test input file
        with open(input_file, 'w') as f:
            f.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")

        # Clean the file (remove first and last lines)
        with patch.object(settings, 'CLEANING_PATTERNS', {'budget_report': [0, -1]}):
            self.processor.clean_dat_file(input_file, output_file)

        # Check output
        with open(output_file, 'r') as f:
            lines = f.readlines()

        self.assertEqual(len(lines), 3)  # Should have 3 lines left


class MasterDataManagerTest(TestCase):
    """Tests for MasterDataManager class."""

    def setUp(self):
        """Set up test data."""
        self.manager = MasterDataManager()

        # Create test WBS elements
        WBSElement.objects.create(wbs_element="P-001", name="Project One")
        WBSElement.objects.create(wbs_element="P-002", name="Project Two")
        WBSElement.objects.create(wbs_element="P-003", name="Project Three")

    def test_check_wbs_data_availability_with_data(self):
        """Test WBS availability check when data exists."""
        is_available, message = self.manager.check_wbs_data_availability()

        self.assertTrue(is_available)
        # Should return a message with count
        self.assertIn("WBS master data loaded", message)
        self.assertIn("3 elements", message)

    def test_check_wbs_data_availability_without_data(self):
        """Test WBS availability check when data is missing."""
        # Clear all WBS elements
        WBSElement.objects.all().delete()

        is_available, message = self.manager.check_wbs_data_availability()

        self.assertFalse(is_available)
        self.assertIn("File", message)  # Should mention file or database

    def test_map_wbs_descriptions_success(self):
        """Test mapping WBS descriptions successfully."""
        # Create a test DataFrame
        test_df = pd.DataFrame({
            ('WBS', 'Code'): ['P-001', 'P-002', 'P-999'],
            ('WBS', 'Description'): ['', '', '']
        })

        result_df = self.manager.map_wbs_descriptions(
            transaction_df=test_df,
            wbs_column=('WBS', 'Code'),
            description_column=('WBS', 'Description')
        )

        # Check that descriptions were mapped
        self.assertEqual(result_df.loc[0, ('WBS', 'Description')], "Project One")
        self.assertEqual(result_df.loc[1, ('WBS', 'Description')], "Project Two")
        # P-999 doesn't exist, should remain empty
        self.assertEqual(result_df.loc[2, ('WBS', 'Description')], "")

    def test_map_wbs_descriptions_no_data(self):
        """Test mapping WBS descriptions when no data in database."""
        # Clear all WBS elements
        WBSElement.objects.all().delete()

        test_df = pd.DataFrame({
            ('WBS', 'Code'): ['P-001'],
            ('WBS', 'Description'): ['']
        })

        # Should not crash, just return unchanged DataFrame
        result_df = self.manager.map_wbs_descriptions(
            transaction_df=test_df,
            wbs_column=('WBS', 'Code'),
            description_column=('WBS', 'Description')
        )

        self.assertEqual(result_df.shape, test_df.shape)

    def test_map_wbs_descriptions_caching(self):
        """Test that WBS availability check is cached."""
        # First call
        self.manager.check_wbs_data_availability()

        # Second call should use cached result
        with patch.object(WBSElement.objects, 'count') as mock_count:
            self.manager.check_wbs_data_availability()
            # Should not call count again due to caching
            mock_count.assert_not_called()


class WBSProcessorTest(TestCase):
    """Tests for WBSProcessor class."""

    def setUp(self):
        """Set up test data."""
        self.processor = WBSProcessor()

        # Create test data
        WBSElement.objects.create(wbs_element="P-100", name="Test Project")
        WBSElement.objects.create(wbs_element="P-100-01", name="Sub Project 1")
        WBSElement.objects.create(wbs_element="P-100-02", name="Sub Project 2")

    def test_wbs_processor_initialization(self):
        """Test that WBSProcessor initializes correctly."""
        self.assertIsNotNone(self.processor)
        self.assertIsInstance(self.processor, WBSProcessor)

    def test_classify_wbs_elements(self):
        """Test classification of WBS elements into summary and transaction."""
        wbs_list = ["P-100", "P-100-01", "P-100-02", "P-200"]

        summary_wbs, transaction_wbs = self.processor.classify_wbs_elements(wbs_list)

        # P-100 should be summary (has children P-100-01, P-100-02)
        self.assertIn("P-100", summary_wbs)
        # P-100-01, P-100-02, P-200 should be transaction (no children)
        self.assertIn("P-100-01", transaction_wbs)
        self.assertIn("P-100-02", transaction_wbs)
        self.assertIn("P-200", transaction_wbs)

    def test_classify_empty_wbs_list(self):
        """Test classification with empty WBS list."""
        summary_wbs, transaction_wbs = self.processor.classify_wbs_elements([])

        self.assertEqual(len(summary_wbs), 0)
        self.assertEqual(len(transaction_wbs), 0)

    def test_parse_wbs_details(self):
        """Test parsing WBS detail strings."""
        # Create a test series with WBS details
        test_series = pd.Series([
            "Level 1: Project Alpha - P-100",
            "Level 2: Sub Project - P-100-01",
            None,  # Test handling of None
            ""  # Test handling of empty string
        ])

        result = self.processor.parse_wbs_details(test_series)

        # Should return a dictionary with lists
        self.assertIsInstance(result, dict)
        self.assertIn('level', result)
        self.assertIn('description', result)
        self.assertIn('id', result)


class MasterDataLoadingTest(TestCase):
    """Tests for master data loading and validation."""

    def setUp(self):
        """Set up test company codes and project types."""
        CompanyCode.objects.create(code="1000", name="Company A")
        CompanyCode.objects.create(code="2000", name="Company B")

        ProjectType.objects.create(code="CAP", name="Capital")
        ProjectType.objects.create(code="OM", name="O&M")

    def test_company_codes_loaded(self):
        """Test that company codes are available."""
        count = CompanyCode.objects.count()
        self.assertEqual(count, 2)

    def test_project_types_loaded(self):
        """Test that project types are available."""
        count = ProjectType.objects.count()
        self.assertEqual(count, 2)

    def test_filter_by_company_code(self):
        """Test filtering data by company code."""
        test_df = pd.DataFrame({
            'Company': ['1000', '2000', '1000', '3000'],
            'Amount': [100, 200, 300, 400]
        })

        # Filter for existing company
        company_1000 = test_df[test_df['Company'] == '1000']
        self.assertEqual(len(company_1000), 2)

        # Filter for non-existing company
        company_3000 = test_df[test_df['Company'] == '3000']
        self.assertEqual(len(company_3000), 1)

    def test_filter_by_project_type(self):
        """Test filtering data by project type."""
        test_df = pd.DataFrame({
            'Type': ['CAP', 'OM', 'CAP', 'DEV'],
            'Amount': [100, 200, 300, 400]
        })

        # Filter for existing type
        capital = test_df[test_df['Type'] == 'CAP']
        self.assertEqual(len(capital), 2)
