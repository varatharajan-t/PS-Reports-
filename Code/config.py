"""
Configuration Management for SAP Project System
Centralizes all configurable parameters for easy maintenance
"""

import os
from pathlib import Path


class Config:
    """Central configuration class for all SAP reporting modules."""

    # File Settings
    TEMP_DAT_FILE = "temp.dat"
    TEMP_HTML_FILE = "temp.html"
    MASTER_WBS_FILE = "data/WBS_NAMES.XLSX"
    ICON_FILE = Path("data/nlcil.png")

    # Excel Formatting
    EXCEL_FONT = {"name": "Bookman Old Style", "size": 12}

    CURRENCY_FORMAT = "₹ #,##0.00;[Red]₹ -#,##0.00"

    # Colors (using constants for consistency)
    COLORS = {
        "header_yellow": "FFFF00",
        "header_bold": "000000",
        "row_sky_blue": "87CEEB",
        "row_white": "FFFFFF",
        "summary_light_green": "90EE90",
        "summary_orange": "FFA500",
    }

    # Business Logic Mappings
    COMPANY_CODES = {
        "NL": "NLCIL",
        "NT": "NTPL",
        "NU": "NUPPL",
        "NR": "NIRL",
        "NG": "NIGEL",
    }

    PROJECT_TYPES = {
        "S": "Service",
        "I": "Income",
        "N": "Non-Plan",
        "C": "Capex",
        "E": "Excetra",
        "F": "Feasibility",
        "R": "R&D",
        "O": "Opex",
        "M": "Material",
    }

    # Data Cleaning Patterns (different for each report type)
    CLEANING_PATTERNS = {
        "budget_report": [0, 1, 4, -1],  # lines to remove
        "budget_updates": [0, 3, -1],
        "html_reports": [0, 1],  # first two lines
    }

    # Regex Patterns
    REGEX_PATTERNS = {
        "project_id": r"PRJ\s+([A-Z0-9-]+)",
        "wbs_child": r"-\d{2}",
        "wbs_levels": r"[\*]{1,5}",
    }

    # Excel Settings
    FREEZE_PANES = {"default": "E3", "analysis": "D3", "summary": "A2"}

    # Error Messages
    ERROR_MESSAGES = {
        "file_not_found": "Required file not found: {}",
        "invalid_format": "Invalid file format. Expected: {}",
        "processing_error": "Error processing data: {}",
        "excel_error": "Error generating Excel file: {}",
    }

    ALLOWED_EXTENSIONS = {
        '.dat': 'DAT files',
        '.html': 'HTML files',
        '.xlsx': 'Excel files',
    }

    # Project Analysis Settings
    PROJECT_ANALYSIS_FILES = {
        "budget": "All_Projects.DAT",
        "plan": "All_Projects_Plan.DAT",
    }
    PROJECT_ANALYSIS_OUTPUT = "ProjectAnalysis.xlsx"
    PROJECT_ANALYSIS_REGEX = {
        "budget": r"6\*\s*(.*?)\s*PRJ(.*)",
        "plan": r"6\*\s*PRJ\s*([A-Za-z0-9\-]{12})\s*(.*)",
    }

    # Year End 558 Settings
    YEAR_END_558_INPUT_FILE = "data/TPP.xlsx"
    YEAR_END_558_OUTPUT_FILE = "data/TPP_YearEnd.xlsx"


    @classmethod
    def get_output_filename(cls, input_filename, suffix=""):
        """Generate standardized output filename."""
        p = Path(input_filename)
        return p.with_name(f"{p.stem}{suffix}").with_suffix(".xlsx")

    @classmethod
    def validate_required_files(cls):
        """Validate all required files exist."""
        required_files = [cls.MASTER_WBS_FILE]
        missing_files = [f for f in required_files if not Path(f).exists()]
        return missing_files
