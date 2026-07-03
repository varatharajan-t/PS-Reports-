"""
Service layer for generating the Glimps of Projects Report from Excel input.
Accepts an All-ProjectIDs.XLSX file (with a 'Project definition' column)
instead of a SAP DAT file. Analysis logic is identical to the DAT-based version.

KEY FEATURES:
- Reads project IDs directly from the 'Project definition' column of an Excel file
- Cross-tabulation matrix analysis (same as DAT-based version)
- Interactive 3D charts (Excel) and Chart.js charts (HTML)
- Dynamic data validation dropdowns
- Company and project type mapping
- Statistical summary with multiple dimensions
"""
import os
import pandas as pd
from pathlib import Path
import openpyxl
from openpyxl.styles import PatternFill, Font
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.chart import BarChart3D, Reference
from openpyxl.chart.series import DataPoint

from django.conf import settings
from .data_processing import BaseDataProcessor
from .error_handling import handle_error

# Reuse HTML/chart generation from the original service
from .glimps_of_projects_service import (
    generate_formatted_html_with_charts,
    GlimpsExcelFormatter,
)

PROJECT_ID_COLUMN = "Project definition"


class GlimpsOfProjectsXlsxProcessor(BaseDataProcessor):
    """Processes project data from an All-ProjectIDs Excel file."""

    def __init__(self, input_file_path: str):
        super().__init__('GlimpsOfProjectsXlsx')
        self.input_file_path = Path(input_file_path)
        self.project_data = []

    def validate_input(self, file_path: str) -> bool:
        """Validate that the uploaded file is a non-empty Excel workbook."""
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path_obj.stat().st_size == 0:
            raise ValueError("The uploaded Excel file is empty")

        if file_path_obj.suffix.lower() not in ['.xlsx', '.xls', '.xlsm']:
            raise ValueError(
                f"Expected an Excel file (.xlsx/.xls/.xlsm), got: {file_path_obj.suffix}"
            )

        self.logger.info(f"Input file validation passed: {file_path}")
        return True

    def process_data(self, file_path: str) -> pd.DataFrame:
        """
        Reads the 'Project definition' column from the Excel file and applies
        the same company-code / project-type extraction as the DAT-based version.

        Project ID format: XX-T-... where XX = company code, T = type at index 3.
        Returns a cross-tabulation DataFrame.
        """
        company_codes = settings.COMPANY_CODES
        project_types = settings.PROJECT_TYPES

        df_raw = pd.read_excel(file_path, engine="openpyxl")

        if PROJECT_ID_COLUMN not in df_raw.columns:
            raise ValueError(
                f"Column '{PROJECT_ID_COLUMN}' not found in the Excel file. "
                f"Available columns: {list(df_raw.columns)}"
            )

        self.project_data = []

        for project_id in df_raw[PROJECT_ID_COLUMN].dropna().astype(str):
            project_id = project_id.strip()
            if not project_id:
                continue

            # Extract company code (first 2 characters, e.g. "NL")
            company_code = project_id[:2]
            company_desc = company_codes.get(company_code, "Unknown Company")

            # Extract project type (4th character, index 3, e.g. "C" in "NL-C-...")
            if len(project_id) > 3:
                project_type_code = project_id[3]
                project_desc = project_types.get(project_type_code, "Unknown Project Type")
            else:
                project_desc = "Unknown Project Type"

            self.project_data.append({
                "Project Type": project_desc,
                "Company": company_desc,
                "Project ID": project_id,
            })

        if not self.project_data:
            raise ValueError(
                f"No valid project IDs found in column '{PROJECT_ID_COLUMN}'"
            )

        df = pd.DataFrame(self.project_data)
        crosstab = pd.crosstab(
            df["Project Type"],
            df["Company"],
            margins=True,
            margins_name="Total"
        )
        return crosstab


@handle_error
def generate_glimps_of_projects_xlsx_report(uploaded_file_path: str) -> dict:
    """
    Orchestrates report generation from an All-ProjectIDs Excel file.
    Returns a dict with the path to the formatted Excel report and HTML dashboard.
    """
    processor = GlimpsOfProjectsXlsxProcessor(uploaded_file_path)
    processor.validate_input(uploaded_file_path)
    crosstab_df = processor.process_data(uploaded_file_path)

    output_filename = "CrossTab_Report_XLSX.xlsx"
    reports_dir = settings.BASE_DIR / 'data' / 'reports'
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = str(reports_dir / output_filename)

    formatter = GlimpsExcelFormatter(crosstab_df, output_path)
    formatted_file_path = formatter.format_and_save()

    chart_output = generate_formatted_html_with_charts(crosstab_df)

    return {
        "file_path": formatted_file_path,
        "data_html": chart_output['html'],
        "chart_script": chart_output['script'],
    }
