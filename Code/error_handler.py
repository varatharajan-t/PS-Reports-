"""
Enhanced Error Handling and Logging System
Provides comprehensive error management with user-friendly feedback
"""

import logging
import logging.handlers
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional, Any
from PySide6.QtWidgets import QMessageBox, QApplication
from config import Config


class SAPReportLogger:
    """Centralized logging system for SAP reporting applications."""

    def __init__(self, module_name: str):
        self.module_name = module_name
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Configure logging with file and console handlers."""
        logger = logging.getLogger(self.module_name)
        logger.setLevel(logging.INFO)

        # Create logs directory if not exists
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # File handler with rotation
        log_file = log_dir / f"sap_reports_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=1024 * 1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def log_info(self, message: str, **kwargs):
        """Log informational message."""
        self.logger.info(f"{message} - {kwargs}")

    def log_warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(f"{message} - {kwargs}")

    def log_error(self, message: str, error: Exception = None, **kwargs):
        """Log error with full traceback."""
        error_msg = f"{message} - {kwargs}"
        if error:
            error_msg += f"\nError: {str(error)}\nTraceback: {traceback.format_exc()}"
        self.logger.error(error_msg)


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
    """Decorator for comprehensive error handling."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            logger = SAPReportLogger(func.__module__)
            logger.log_error("File not found", e, function=func.__name__)
            show_error_dialog(
                "File Not Found",
                f"Required file not found: {str(e)}",
                "Please ensure all required files are in the correct directory.",
            )
            raise FileProcessingError(f"File not found: {str(e)}", "FILE_NOT_FOUND", e)

        except PermissionError as e:
            logger = SAPReportLogger(func.__module__)
            logger.log_error("Permission denied", e, function=func.__name__)
            show_error_dialog(
                "Permission Error",
                "Unable to access file due to permission restrictions.",
                "Please check file permissions or close any open Excel files.",
            )
            raise FileProcessingError(
                f"Permission denied: {str(e)}", "PERMISSION_DENIED", e
            )

        except Exception as e:
            logger = SAPReportLogger(func.__module__)
            logger.log_error("Unexpected error", e, function=func.__name__)
            show_error_dialog(
                "Unexpected Error",
                f"An unexpected error occurred: {str(e)}",
                "Please check the log files for detailed error information.",
            )
            raise SAPReportError(
                f"Unexpected error in {func.__name__}: {str(e)}", "UNEXPECTED_ERROR", e
            )

    return wrapper


def show_error_dialog(title: str, message: str, details: str = None):
    """Display user-friendly error dialog."""
    if QApplication.instance() is None:
        print(f"ERROR: {title} - {message}")
        if details:
            print(f"Details: {details}")
        return

    try:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        if details:
            msg_box.setDetailedText(details)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
    except Exception as e:
        print(f"ERROR: {title} - {message}")
        if details:
            print(f"Details: {details}")
        print(f"GUI Error: {e}")


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
