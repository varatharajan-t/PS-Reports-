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
    MASTER_PROJECTS_FILE = "data/All_Projects.XLSX"
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

    # CJI3 Document Types
    DOCUMENT_TYPES = {
        "AA": "Asset Posting",
        "AB": "Accounting Document",
        "AF": "Depreciation Pstngs",
        "AL": "Allocation Document",
        "AN": "Net Asset Posting",
        "AR": "Allocation Reversal",
        "CH": "Contract Settlement",
        "CJ": "Cash Journal",
        "CZ": "Cheque Payment",
        "D1": "EMD RECEIPT IN NEAT",
        "DA": "Customer Document",
        "DG": "Customer Credit Memo",
        "DR": "Customer Invoice",
        "DZ": "Customer Payment",
        "EU": "Euro Rounding Diff.",
        "EX": "External Number",
        "IG": "Integration CO->FI",
        "IN": "INB Payment",
        "IS": "G/L Account Document",
        "IU": "G/L Account Document",
        "K1": "EMD RECEIPT IN NEAT",
        "KA": "Vendor Document",
        "KE": "Emp Vendor Invoice",
        "KG": "Vendor Credit Memo",
        "KN": "Net Vendors",
        "KP": "Account Maintenance",
        "KR": "Vendor Invoice",
        "KZ": "Vendor Payment",
        "M1": "MINE I Interface",
        "M2": "MINE II Interface",
        "M3": "P&L Lock",
        "M4": "P&L Close",
        "M5": "P&L Transformation",
        "M6": "FX Valuation",
        "M7": "MAR & Restatement",
        "M8": "IFX Correction",
        "M9": "Reversal",
        "MD": "Data Load",
        "ME": "MEMMS Doc Type",
        "ML": "ML Settlement",
        "MM": "OLIMMS Doc Type",
        "NL": "NL Ledger Postings",
        "OB": "Opening Bal. Upload",
        "OS": "Op.Bal. init. Stock",
        "OV": "Op.Bal. Vendor",
        "P1": "Payroll Step 5 (Bank",
        "P2": "Payroll Step 2(a)",
        "P3": "Payroll Step 3",
        "P4": "Payroll Step 4",
        "P5": "DRF IUT Posting",
        "P7": "NUPPL Payment IUT",
        "PI": "PF Interest",
        "PR": "Price Change",
        "PT": "Power Trading",
        "PY": "Payroll Documents",
        "PZ": "PowerTradingReceipt",
        "RA": "Sub.Cred.Memo Stlmt",
        "RB": "Reserve for Bad Debt",
        "RE": "Invoice - Gross",
        "RI": "Rent Interface",
        "RN": "Invoice - Net",
        "RR": "Rent Receipts",
        "RT": "Retention Vendor Inv",
        "RV": "Billing Doc.Transfer",
        "RW": "Customer Debit Note",
        "RZ": "RENTAL INVOICE",
        "SA": "G/L Account Document",
        "SB": "G/L Account Posting",
        "SK": "Cash Document",
        "SU": "Adjustment Document",
        "SW": "Adjustment Document",
        "T1": "Trust Transaction",
        "T2": "Trust Transfer",
        "T3": "Trust Settlement",
        "TA": "Treasury for Posting",
        "TB": "G/L Document",
        "TI": "TReDS Inv Document",
        "TR": "Treasury for Reversa",
        "UE": "Data Transfer",
        "UT": "Inter Unit Entries",
        "WA": "Goods Issue",
        "WE": "Goods Receipt",
        "WI": "Inventory Document",
        "WL": "Goods Issue/Delivery",
        "WN": "Net Goods Receipt",
        "ZA": "Value transfer-CWIP",
        "ZI": "Interface Doc Type",
        "ZM": "Maint Ord Settlement",
        "ZP": "Payment Posting",
        "ZR": "Bank Reconciliation",
        "ZS": "Payment by Check",
        "ZT": "Value Reduction",
        "ZV": "Payroll JV",
        "ZW": "WBS Settlement",
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
        "plan": r"5\*\s*PRJ\s*([A-Za-z0-9\-]{12})\s*(.*)",
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
