"""
Enhanced Error Handling and Logging System for Django
Provides comprehensive error management for the reports services.
"""

import logging
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional, Any

# This file is adapted from the original error_handler.py for use in a Django environment.
# The GUI-specific components (PySide6) have been removed.

class SAPReportError(Exception):
    """Base exception for SAP reporting operations."""

    def __init__(
        self, message: str, error_code: str = None, original_error: Exception = None
    ):
        self.message = message
        self.error_code = error_code
        self.original_error = original_error
        super().__init__(self.message)


class FileProcessingError(SAPReportError):
    """Exception raised during file processing operations."""

    pass


class DataValidationError(SAPReportError):
    """Exception raised during data validation."""

    pass


class ExcelGenerationError(SAPReportError):
    """Exception raised during Excel file generation."""

    pass


def handle_error(func):
    """
    Decorator for comprehensive error handling.
    In the Django context, this decorator logs errors and re-raises them
    to be handled by Django's exception middleware.
    """
    logger = logging.getLogger(func.__module__)

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (FileProcessingError, DataValidationError, ExcelGenerationError) as e:
            logger.error(f"A known error occurred in {func.__name__}: {e.message}", exc_info=True)
            raise  # Re-raise the custom exception
        except FileNotFoundError as e:
            logger.error(f"File not found in {func.__name__}: {str(e)}", exc_info=True)
            raise FileProcessingError(f"File not found: {str(e)}", "FILE_NOT_FOUND", e) from e
        except PermissionError as e:
            logger.error(f"Permission denied in {func.__name__}: {str(e)}", exc_info=True)
            raise FileProcessingError(f"Permission denied: {str(e)}", "PERMISSION_DENIED", e) from e
        except Exception as e:
            logger.error(f"An unexpected error occurred in {func.__name__}: {str(e)}", exc_info=True)
            raise SAPReportError(f"An unexpected error in {func.__name__}: {str(e)}", "UNEXPECTED_ERROR", e) from e

    return wrapper


def validate_file_exists(file_path: str, file_description: str = "File"):
    """Validate that a file exists and is readable."""
    path = Path(file_path)
    if not path.exists():
        raise FileProcessingError(
            f"{file_description} not found: {file_path}", "FILE_NOT_FOUND"
        )
    if not path.is_file():
        raise FileProcessingError(
            f"{file_description} is not a valid file: {file_path}", "INVALID_FILE"
        )
    return True


def validate_data_format(df, expected_columns: list = None, min_rows: int = 1):
    """Validate DataFrame format and content."""
    if df is None:
        raise DataValidationError("DataFrame is None", "NULL_DATAFRAME")

    if len(df) < min_rows:
        raise DataValidationError(
            f"Insufficient data rows. Expected: {min_rows}, Found: {len(df)}",
            "INSUFFICIENT_DATA",
        )

    if expected_columns and not all(col in df.columns for col in expected_columns):
        missing_cols = [col for col in expected_columns if col not in df.columns]
        raise DataValidationError(
            f"Missing required columns: {missing_cols}", "MISSING_COLUMNS"
        )

    return True

# The SAPReportLogger class is removed. We will use Django's built-in logging.
# The show_error_dialog function is removed as it's a GUI component.
