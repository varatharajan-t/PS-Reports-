"""
Comprehensive Unit Testing Framework for SAP Project System
"""

import unittest
import pandas as pd
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_processor_base import BaseDataProcessor, WBSProcessor, MasterDataManager
from config import Config
from error_handler import SAPReportError, FileProcessingError, DataValidationError


class TestConfig(unittest.TestCase):
    """Test configuration management."""

    def setUp(self):
        self.config = Config()

    def test_company_codes_mapping(self):
        """Test company codes are properly mapped."""
        self.assertEqual(self.config.COMPANY_CODES["NL"], "NLCIL")
        self.assertEqual(self.config.COMPANY_CODES["NT"], "NTPL")
        self.assertIn("NG", self.config.COMPANY_CODES)

    def test_project_types_mapping(self):
        """Test project types are properly mapped."""
        self.assertEqual(self.config.PROJECT_TYPES["C"], "Capex")
        self.assertEqual(self.config.PROJECT_TYPES["S"], "Service")
        self.assertIn("R", self.config.PROJECT_TYPES)

    def test_output_filename_generation(self):
        """Test output filename generation."""
        result = self.config.get_output_filename("test.dat", "_processed")
        self.assertEqual(result, Path("test_processed.xlsx"))


class TestWBSProcessor(unittest.TestCase):
    """Test WBS processing functionality."""

    def setUp(self):
        self.processor = WBSProcessor()

    def test_classify_wbs_elements_basic(self):
        """Test basic WBS classification."""
        wbs_list = ["PRJ001", "PRJ001-01", "PRJ001-02", "PRJ002"]
        summary, transaction = self.processor.classify_wbs_elements(wbs_list)

        self.assertIn("PRJ001", summary)  # Has children
        self.assertIn("PRJ002", transaction)  # No children
        self.assertIn("PRJ001-01", transaction)  # Child element
        self.assertIn("PRJ001-02", transaction)  # Child element

    def test_classify_wbs_elements_empty(self):
        """Test WBS classification with empty list."""
        summary, transaction = self.processor.classify_wbs_elements([])
        self.assertEqual(len(summary), 0)
        self.assertEqual(len(transaction), 0)

    def test_classify_wbs_elements_with_nulls(self):
        """Test WBS classification handling null values."""
        wbs_list = ["PRJ001", None, "", "PRJ001-01", pd.NA]
        summary, transaction = self.processor.classify_wbs_elements(wbs_list)

        self.assertIn("PRJ001", summary)
        self.assertIn("PRJ001-01", transaction)
        self.assertEqual(len(summary) + len(transaction), 2)  # Only valid entries

    def test_parse_wbs_details(self):
        """Test WBS detail parsing."""
        details_series = pd.Series(
            ["*** Project A PRJ001", "** Task B PRJ001-01", "Invalid format", ""]
        )

        result = self.processor.parse_wbs_details(details_series)

        self.assertEqual(len(result["level"]), 4)
        self.assertEqual(result["level"][0], "***")
        self.assertEqual(result["id"][0], "PRJ001")
        self.assertEqual(result["description"][0], "Project A")


class TestMasterDataManager(unittest.TestCase):
    """Test master data management."""

    def setUp(self):
        self.manager = MasterDataManager()

    def test_load_master_data_cache(self):
        """Test master data caching."""
        # Create temporary Excel file
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            test_data = pd.DataFrame(
                {
                    "WBS_element": ["PRJ001", "PRJ002"],
                    "Name": ["Project One", "Project Two"],
                }
            )
            test_data.to_excel(tmp.name, index=False)
            tmp_path = tmp.name

        try:
            # First load
            df1 = self.manager.load_master_data(tmp_path)
            self.assertEqual(len(df1), 2)

            # Second load (should use cache)
            df2 = self.manager.load_master_data(tmp_path)
            self.assertTrue(df1.equals(df2))
            self.assertIn(tmp_path, self.manager._master_data_cache)

        finally:
            os.unlink(tmp_path)

    def test_map_wbs_descriptions(self):
        """Test WBS description mapping."""
        # Setup test data
        master_data = pd.DataFrame(
            {
                "WBS_element": ["PRJ001", "PRJ002"],
                "Name": ["Project One", "Project Two"],
            }
        )

        transaction_data = pd.DataFrame(
            {"wbs_id": ["PRJ001", "PRJ003", "PRJ002"], "description": ["", "", ""]}
        )

        # Mock the load_master_data method
        with patch.object(self.manager, "load_master_data", return_value=master_data):
            result = self.manager.map_wbs_descriptions(
                transaction_data, "wbs_id", "description"
            )

            self.assertEqual(result.loc[0, "description"], "Project One")
            self.assertEqual(result.loc[2, "description"], "Project Two")
            self.assertEqual(result.loc[1, "description"], "")  # Not found


class TestErrorHandling(unittest.TestCase):
    """Test error handling and validation."""

    def test_file_processing_error(self):
        """Test file processing error creation."""
        error = FileProcessingError("Test message", "TEST_CODE")
        self.assertEqual(error.message, "Test message")
        self.assertEqual(error.error_code, "TEST_CODE")

    def test_data_validation_error(self):
        """Test data validation error creation."""
        error = DataValidationError("Validation failed", "VALIDATION_ERROR")
        self.assertIsInstance(error, SAPReportError)
        self.assertEqual(error.error_code, "VALIDATION_ERROR")


class IntegrationTests(unittest.TestCase):
    """Integration tests for complete workflows."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Clean up test directory
        import shutil

        shutil.rmtree(self.test_dir)

    def test_complete_dat_processing_workflow(self):
        """Test complete DAT file processing workflow."""
        # Create test DAT file
        test_data = """Header Line 1
Header Line 2
WBS_Elements_Info	Object	Value1	Value2
Metadata Line
*** Project A	PRJ001	1000	2000
** Task B	PRJ001-01	500	1000
Footer Line"""

        dat_file = os.path.join(self.test_dir, "test.dat")
        with open(dat_file, "w") as f:
            f.write(test_data)

        # Create mock processor
        class MockProcessor(BaseDataProcessor):
            def validate_input(self, file_path):
                return True

            def process_data(self, file_path):
                return pd.DataFrame({"test": [1, 2, 3]})

        processor = MockProcessor("TestModule")

        # Test cleaning
        cleaned_file = os.path.join(self.test_dir, "cleaned.dat")
        processor.clean_dat_file(dat_file, cleaned_file, "budget_report")

        # Verify file was cleaned
        with open(cleaned_file, "r") as f:
            cleaned_content = f.read()

        self.assertNotIn("Header Line 1", cleaned_content)
        self.assertNotIn("*** Project A", cleaned_content)
        self.assertIn("** Task B", cleaned_content)
        self.assertNotIn("Footer Line", cleaned_content)


class PerformanceTests(unittest.TestCase):
    """Performance tests for optimization validation."""

    def test_large_wbs_classification_performance(self):
        """Test WBS classification performance with large datasets."""
        import time

        # Generate large WBS list
        wbs_list = []
        for i in range(1000):
            wbs_list.append(f"PRJ{i:03d}")
            if i % 10 == 0:  # Every 10th project has children
                for j in range(5):
                    wbs_list.append(f"PRJ{i:03d}-{j:02d}")

        processor = WBSProcessor()

        start_time = time.time()
        summary, transaction = processor.classify_wbs_elements(wbs_list)
        end_time = time.time()

        processing_time = end_time - start_time

        # Should process 1000+ elements in under 1 second
        self.assertLess(
            processing_time,
            1.0,
            f"Processing took {processing_time:.3f} seconds, expected < 1.0",
        )

        # Verify results
        self.assertGreater(len(summary), 0)
        self.assertGreater(len(transaction), 0)
        self.assertEqual(len(summary) + len(transaction), len(set(wbs_list)))


class MockDataTests(unittest.TestCase):
    """Tests using mock data for isolated testing."""

    @patch("pandas.read_csv")
    def test_dat_file_reading_with_encoding_error(self, mock_read_csv):
        """Test DAT file reading with encoding issues."""
        # Mock encoding error
        mock_read_csv.side_effect = UnicodeDecodeError(
            "utf-8", b"", 0, 1, "invalid start byte"
        )

        class TestProcessor(BaseDataProcessor):
            def validate_input(self, file_path):
                return True

            def process_data(self, file_path):
                return pd.DataFrame()

        processor = TestProcessor("TestModule")

        with self.assertRaises(Exception):
            processor.read_dat_file("fake_file.dat")

    @patch("openpyxl.load_workbook")
    def test_excel_formatting_with_mock(self, mock_load_workbook):
        """Test Excel formatting with mocked workbook."""
        from excel_formatter_enhanced import StandardReportFormatter

        # Mock workbook and worksheet
        mock_workbook = MagicMock()
        mock_worksheet = MagicMock()
        mock_worksheet.max_row = 100
        mock_worksheet.max_column = 10
        mock_workbook.active = mock_worksheet

        mock_load_workbook.return_value = mock_workbook

        formatter = StandardReportFormatter("fake_file.xlsx")
        formatter.apply_all_formatting()
        formatter.save()

        # Verify workbook operations were called
        mock_load_workbook.assert_called_once()
        mock_workbook.save.assert_called_once()


def run_all_tests():
    """Run all test suites."""
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestConfig,
        TestWBSProcessor,
        TestMasterDataManager,
        TestErrorHandling,
        IntegrationTests,
        PerformanceTests,
        MockDataTests,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    return result.wasSuccessful()


def run_specific_test(test_name: str):
    """Run a specific test by name."""
    suite = unittest.TestLoader().loadTestsFromName(test_name)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == "__main__":
    # Run all tests if called directly
    success = run_all_tests()

    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
