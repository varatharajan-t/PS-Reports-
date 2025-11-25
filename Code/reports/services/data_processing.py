"""Base Data Processing Framework
Provides consistent data processing patterns across all modules
"""

from django.conf import settings
import logging
import pandas as pd
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from .error_handling import (
    handle_error,
    validate_file_exists,
    validate_data_format,
    FileProcessingError,
    DataValidationError,
)
from ..models import WBSElement


class BaseDataProcessor(ABC):
    """Abstract base class for all data processors."""

    def __init__(self, module_name: str):
        self.module_name = module_name
        self.logger = logging.getLogger(module_name)
        self.df: Optional[pd.DataFrame] = None

    @abstractmethod
    def validate_input(self, file_path: str) -> bool:
        """Validate input file format and content."""
        pass

    @abstractmethod
    def process_data(self, file_path: str) -> pd.DataFrame:
        """Process the input data and return cleaned DataFrame."""
        pass

    @handle_error
    def read_dat_file(
        self,
        file_path: str,
        delimiter: str = "\t",
        header_rows: List[int] = [0, 1],
        encoding: str = "iso-8859-1",
    ) -> pd.DataFrame:
        """
        Standardized DAT file reading with comprehensive validation.

        Args:
            file_path: Path to DAT file
            delimiter: Field separator
            header_rows: List of header row indices
            encoding: File encoding

        Returns:
            pd.DataFrame: Processed DataFrame with multi-level headers
        """
        validate_file_exists(file_path, "DAT file")

        self.logger.info(f"Reading DAT file: {file_path}, encoding: {encoding}")

        try:
            df = pd.read_csv(
                file_path,
                sep=delimiter,
                header=header_rows,
                encoding=encoding,
                low_memory=False,
            )

            # Convert multi-level columns to tuples
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.map(lambda x: tuple(map(str, x)))

            validate_data_format(df, min_rows=1)
            self.logger.info(
                f"Successfully read DAT file: {len(df)} rows, {len(df.columns)} columns"
            )

            return df

        except pd.errors.EmptyDataError:
            raise FileProcessingError("DAT file is empty", "EMPTY_FILE")
        except pd.errors.ParserError as e:
            raise FileProcessingError(
                f"Error parsing DAT file: {str(e)}", "PARSE_ERROR", e
            )

    @handle_error
    def clean_dat_file(
        self,
        input_file: str,
        output_file: str,
        cleaning_pattern: str = "budget_report",
    ) -> None:
        """
        Clean DAT file by removing unnecessary lines.

        Args:
            input_file: Path to input DAT file
            output_file: Path for cleaned output file
            cleaning_pattern: Type of cleaning pattern to apply
        """
        validate_file_exists(input_file, "Input DAT file")

        lines_to_remove = settings.CLEANING_PATTERNS.get(
            cleaning_pattern, settings.CLEANING_PATTERNS["budget_report"]
        )

        self.logger.info(
            f"Cleaning DAT file: {input_file} -> {output_file}, pattern: {cleaning_pattern}"
        )

        try:
            with open(input_file, "r", encoding="utf-8", errors="ignore") as file:
                lines = file.readlines()

            total_lines = len(lines)
            if total_lines == 0:
                raise FileProcessingError("Input file is empty", "EMPTY_FILE")

            # Handle negative indices (from end)
            indices_to_remove = set()
            for idx in lines_to_remove:
                if idx < 0:
                    indices_to_remove.add(total_lines + idx)
                else:
                    indices_to_remove.add(idx)

            cleaned_lines = [
                line for i, line in enumerate(lines) if i not in indices_to_remove
            ]

            with open(output_file, "w", encoding="utf-8") as file:
                file.writelines(cleaned_lines)

            self.logger.info(
                f"DAT file cleaned successfully: {total_lines} -> {len(cleaned_lines)} lines"
            )

        except Exception as e:
            raise FileProcessingError(
                f"Error cleaning DAT file: {str(e)}", "CLEANING_ERROR", e
            )


class WBSProcessor:
    """Enhanced WBS (Work Breakdown Structure) processing utilities."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @handle_error
    def classify_wbs_elements(self, wbs_list: List[str]) -> Tuple[List[str], List[str]]:
        """
        Classify WBS elements into summary and transaction categories.

        Args:
            wbs_list: List of WBS element identifiers

        Returns:
            Tuple of (summary_wbs, transaction_wbs) lists
        """
        if not wbs_list:
            self.logger.warning("Empty WBS list provided")
            return [], []

        summary_wbs = []
        transaction_wbs = []

        # Remove duplicates while preserving order
        unique_wbs = list(dict.fromkeys(wbs_list))

        self.logger.info(f"Classifying WBS elements: {len(unique_wbs)} total elements")

        for wbs in unique_wbs:
            if not wbs or pd.isna(wbs):
                continue

            wbs_str = str(wbs).strip()
            if not wbs_str:
                continue

            # Create regex pattern for child detection
            pattern = re.compile(
                re.escape(wbs_str) + settings.REGEX_PATTERNS["wbs_child"]
            )

            # Check for child elements
            has_child = any(
                pattern.fullmatch(str(item).strip())
                for item in unique_wbs
                if item != wbs and item and not pd.isna(item)
            )

            if has_child:
                summary_wbs.append(wbs_str)
            else:
                transaction_wbs.append(wbs_str)

        self.logger.info(
            f"WBS classification completed: {len(summary_wbs)} summary, {len(transaction_wbs)} transaction"
        )

        return summary_wbs, transaction_wbs

    @handle_error
    def parse_wbs_details(self, wbs_detail_series: pd.Series) -> Dict[str, List[str]]:
        """
        Parse WBS detail strings into structured components.

        Args:
            wbs_detail_series: Pandas series containing WBS detail strings

        Returns:
            Dictionary with 'level', 'description', and 'id' lists
        """
        levels = []
        descriptions = []
        ids = []

        level_patterns = settings.REGEX_PATTERNS["wbs_levels"]

        for detail in wbs_detail_series:
            if pd.isna(detail) or not str(detail).strip():
                levels.append("")
                descriptions.append("")
                ids.append("")
                continue

            # Split detail string
            parts = str(detail).split()
            if len(parts) < 2:
                levels.append("")
                descriptions.append(str(detail))
                ids.append("")
                continue

            level = parts[0]
            description = " ".join(parts[1:-1]) if len(parts) > 2 else ""
            wbs_id = parts[-1]

            # Check if level matches pattern
            if not re.match(level_patterns, level):
                description = level + " " + description
                level = ""

            levels.append(level)
            descriptions.append(description)
            ids.append(wbs_id)

        return {"level": levels, "description": descriptions, "id": ids}


class MasterDataManager:
    """Manages master data integration and mapping."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @handle_error
    def map_wbs_descriptions(
        self, transaction_df: pd.DataFrame, wbs_column: str, description_column: str
    ) -> pd.DataFrame:
        """
        Map WBS descriptions using the WBSElement model from the database.

        Args:
            transaction_df: DataFrame containing transaction data
            wbs_column: Name of WBS ID column
            description_column: Name of description column to update

        Returns:
            pd.DataFrame: Updated DataFrame with mapped descriptions
        """
        self.logger.info("Fetching WBS master data from database...")
        
        # Create mapping dictionary directly from the Django model
        mapping_dict = dict(WBSElement.objects.values_list('wbs_element', 'name'))
        
        if not mapping_dict:
            self.logger.warning("WBS master data is empty. No descriptions will be mapped.")
            return transaction_df

        # Apply mapping
        if wbs_column in transaction_df.columns:
            transaction_df[description_column] = (
                transaction_df[wbs_column]
                .map(mapping_dict)
                .fillna(transaction_df.get(description_column, ""))
            )

            mapped_count = transaction_df[description_column].notna().sum()
            self.logger.info(
                "WBS descriptions mapped",
                total_rows=len(transaction_df),
                mapped_rows=mapped_count,
            )

        return transaction_df
