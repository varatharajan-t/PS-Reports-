"""
IMPROVED VERSION: BudgetReport.py
Demonstrates how to refactor existing code with new framework
"""

import os
import sys
from pathlib import Path
from typing import Tuple, List, Optional

# Import new framework components
from config import Config
from error_handler import SAPReportLogger, handle_error, validate_file_exists
from data_processor_base import BaseDataProcessor, WBSProcessor, MasterDataManager
from excel_formatter_enhanced import StandardReportFormatter


class ImprovedBudgetReportProcessor(BaseDataProcessor):
    """Improved budget report processor using new framework."""

    def __init__(self):
        super().__init__("BudgetReportProcessor")
        self.wbs_processor = WBSProcessor()
        self.master_data_manager = MasterDataManager()
        self.config = Config()

    def validate_input(self, file_path: str) -> bool:
        """Validate input DAT file."""
        validate_file_exists(file_path, "Budget DAT file")

        # Additional validation specific to budget reports
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            first_lines = [f.readline().strip() for _ in range(3)]

        # Check for expected structure
        if not any("WBS" in line for line in first_lines):
            raise DataValidationError(
                "File does not appear to be a valid budget report", "INVALID_FORMAT"
            )

        return True

    @handle_error
    def process_data(self, file_path: str) -> pd.DataFrame:
        """Process budget report data with comprehensive error handling."""
        # Step 1: Validate input
        self.validate_input(file_path)

        # Step 2: Clean the data file
        cleaned_file = self.config.TEMP_DAT_FILE
        self.clean_dat_file(file_path, cleaned_file, "budget_report")

        # Step 3: Read cleaned data
        df = self.read_dat_file(cleaned_file)

        # Step 4: Transform WBS structure
        df = self._transform_wbs_structure(df)

        # Step 5: Map descriptions
        df = self.master_data_manager.map_wbs_descriptions(
            df, ("WBS_Elements_Info.", "ID_No"), ("WBS_Elements_Info.", "Description")
        )

        # Step 6: Classify WBS elements
        wbs_ids = df[("WBS_Elements_Info.", "ID_No")].tolist()
        summary_wbs, transaction_wbs = self.wbs_processor.classify_wbs_elements(wbs_ids)

        # Step 7: Flatten MultiIndex columns for Excel compatibility
        df.columns = [' - '.join(col).strip() if isinstance(col, tuple) else str(col) for col in df.columns]

        # Add serial number column at the beginning
        df.insert(0, 'Sl No.', range(1, len(df) + 1))

        self.logger.log_info(
            "Data processing completed",
            rows=len(df),
            summary_wbs=len(summary_wbs),
            transaction_wbs=len(transaction_wbs),
        )

        return df, summary_wbs

    def _transform_wbs_structure(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform WBS structure with improved error handling."""
        try:
            # Rename first column
            df = df.rename(columns={"Unnamed: 0_level_0": "WBS_Elements_Info."})

            # Process WBS details
            if ("WBS_Elements_Info.", "Object") not in df.columns:
                raise DataValidationError(
                    "Missing required WBS Object column", "MISSING_WBS_COLUMN"
                )

            wbs_details = df[("WBS_Elements_Info.", "Object")]
            parsed_details = self.wbs_processor.parse_wbs_details(wbs_details)

            # Add parsed columns
            df[("WBS_Elements_Info.", "Level")] = parsed_details["level"]
            df[("WBS_Elements_Info.", "Description")] = parsed_details["description"]
            df[("WBS_Elements_Info.", "ID_No")] = parsed_details["id"]

            # Reorganize columns
            wbs_cols = [
                ("WBS_Elements_Info.", "Level"),
                ("WBS_Elements_Info.", "Description"),
                ("WBS_Elements_Info.", "ID_No"),
            ]
            other_cols = [col for col in df.columns if col not in wbs_cols]
            df = df[wbs_cols + other_cols]

            return df

        except Exception as e:
            raise DataValidationError(
                f"Error transforming WBS structure: {str(e)}", "WBS_TRANSFORM_ERROR", e
            )


class ImprovedBudgetReportGenerator:
    """Main generator class orchestrating the entire process."""

    def __init__(self):
        self.logger = SAPReportLogger("BudgetReportGenerator")
        self.config = Config()

    @handle_error
    def generate_report(
        self, file_path: str = None, progress_callback: callable = None
    ) -> str:
        """
        Generate budget report with comprehensive error handling.

        Args:
            file_path: Optional file path, will prompt if not provided
            progress_callback: Optional callback for progress updates

        Returns:
            str: Path to generated Excel file
        """
        try:
            # Update progress
            if progress_callback:
                progress_callback(10, "Initializing report generation...")

            # Step 1: File selection
            if not file_path:
                file_path, file_name = self._get_file_selection()
            else:
                file_path, file_name = os.path.split(file_path)

            if not file_path or not file_name:
                raise FileProcessingError("No file selected", "NO_FILE_SELECTED")

            os.chdir(file_path)

            if progress_callback:
                progress_callback(20, "File selected, processing data...")

            # Step 2: Process data
            processor = ImprovedBudgetReportProcessor()
            full_file_path = os.path.join(file_path, file_name)
            processed_df, summary_wbs = processor.process_data(full_file_path)

            if progress_callback:
                progress_callback(60, "Data processed, generating Excel...")

            # Step 3: Generate Excel output
            output_file = self.config.get_output_filename(file_name)
            processed_df.to_excel(output_file, index=False)

            # Step 4: Add headers
            self._add_excel_headers(output_file)

            if progress_callback:
                progress_callback(80, "Applying Excel formatting...")

            # Step 5: Apply formatting
            formatter = StandardReportFormatter(
                str(output_file), "BudgetReportFormatter"
            )
            formatter.apply_all_formatting(summary_wbs)
            formatter.save()

            if progress_callback:
                progress_callback(100, "Report generation completed!")

            self.logger.log_info(
                "Budget report generated successfully",
                input_file=file_name,
                output_file=str(output_file),
            )

            return str(output_file)

        except Exception as e:
            self.logger.log_error("Report generation failed", e)
            raise

    def _get_file_selection(self) -> Tuple[str, str]:
        """Get file selection with improved error handling."""
        from PySide6.QtWidgets import QFileDialog, QApplication

        # Ensure QApplication exists
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        filepath, _ = QFileDialog.getOpenFileName(
            None,
            "Select Budget Report DAT File",
            "",
            "DAT Files(*.DAT);;All Files(*.*)",
        )

        if not filepath:
            return None, None

        return os.path.split(filepath)

    @handle_error
    def _add_excel_headers(self, excel_file: str):
        """
        Placeholder method - serial number column is now added during data transformation.
        Kept for backward compatibility.
        """
        self.logger.log_info("Serial number column added during data processing")


def main():
    """Main function with improved error handling and logging."""
    try:
        generator = ImprovedBudgetReportGenerator()
        output_file = generator.generate_report()

        print(f"✅ Budget report generated successfully: {output_file}")

    except KeyboardInterrupt:
        print("⚠️  Report generation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Report generation failed: {str(e)}")
        print("Check log files for detailed error information")
        sys.exit(1)


if __name__ == "__main__":
    main()
