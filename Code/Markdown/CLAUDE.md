# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an SAP Project System reporting suite that processes SAP data exports (DAT files and HTML) and converts them into professionally formatted Excel reports with analytics, dashboards, and interactive visualizations. The system focuses on Work Breakdown Structure (WBS) analysis, budget tracking, variance reporting, and project classification.

## Common Development Commands

### Running the Application

```bash
# Run the main menu (PySide6 version)
python MenuPySide1.py

# Run the Tkinter menu
python menu.py

# Run individual report modules directly
python BudgetReport.py
python BudgetUpdates.py
python PlanVariance.py
python BudgetVariance.py
python GlimpsOfProjects.py
python ProjectAnalysis.py
python ProjectTypeWise.py
```

### Testing

```bash
# Run all tests
python -m unittest test_framework.py

# Run specific test class
python -m unittest test_framework.TestWBSProcessor

# Run with verbose output
python -m unittest test_framework.py -v
```

### Dependencies

Python 3.7+ with the following packages:
- `pandas >= 1.3.0` - Data processing
- `openpyxl >= 3.0.0` - Excel generation with chart support
- `PySide6 >= 6.0.0` - GUI framework

Install dependencies:
```bash
pip install pandas openpyxl PySide6
```

## Architecture

### Core Design Pattern

The codebase follows a consistent three-layer architecture across all report modules:

1. **FileHandler** - File selection and path management (uses PySide6 QFileDialog)
2. **DataProcessor** - Data cleaning, transformation, and WBS classification
3. **ExcelFormatter** - Professional Excel styling, formatting, and chart generation

### Module Categories

**Core Processing Files**: Transform SAP data into Excel reports
- `BudgetReport.py` - Standard budget processing
- `BudgetUpdates.py` - Budget modification tracking (enhanced WBS processing)
- `BudgetVariance.py` - Budget vs actual variance (processes HTML input)
- `PlanVariance.py` - Plan vs execution variance
- `GlimpsOfProjects.py` - Interactive analytics dashboard with 3D charts
- `ProjectAnalysis.py` - Multi-file processing with merge operations
- `ProjectTypeWise.py` - Project classification with hyperlinked navigation
- `YearEnd558.py` - Year-end financial extraction using pandas IndexSlice

**UI Files**: Menu systems for launching report modules
- `menu.py` - Tkinter-based menu (cross-platform)
- `menuPyside.py` - Simplified PySide6 menu
- `MenuPySide1.py` - Advanced PySide6 menu with custom styling

**Framework Files**: Shared infrastructure
- `config.py` - Centralized configuration (business logic mappings, colors, regex patterns)
- `data_processor_base.py` - Abstract base classes and shared processing utilities
- `error_handler.py` - Comprehensive error handling with logging and user dialogs
- `excel_formatter_enhanced.py` - Base Excel formatting framework
- `test_framework.py` - Unit testing infrastructure

### Critical WBS Classification Algorithm

The WBS (Work Breakdown Structure) classification is a core algorithm used throughout the system:

```python
# Location: data_processor_base.py:140 (WBSProcessor.classify_wbs_elements)
# Pattern: Identifies parent-child relationships using regex
# Example: "NL-C-001" is a parent if "NL-C-001-01" exists in the list
pattern = re.compile(re.escape(wbs_str) + r"-\d{2}")
has_child = any(pattern.fullmatch(item) for item in unique_wbs if item != wbs)
```

WBS elements are classified as:
- **Summary WBS**: Elements with child elements (highlighted in reports)
- **Transaction WBS**: Leaf elements with actual transactions

### Data Processing Pipeline

Standard workflow across modules:

```
1. File Selection (QFileDialog)
   ↓
2. Data Cleaning (remove SAP metadata lines)
   ↓
3. Data Reading (pandas with multi-level headers)
   ↓
4. WBS Processing (split, classify, map descriptions)
   ↓
5. Master Data Mapping (WBS_NAMES.XLSX lookup)
   ↓
6. Excel Generation (openpyxl with formatting)
   ↓
7. Error Handling (logging to logs/ directory)
```

### Business Logic Mappings

Company codes and project types are centralized in `config.py`:

```python
COMPANY_CODES = {
    "NL": "NLCIL",   # Neyveli Lignite Corporation India Limited
    "NT": "NTPL",    # NLC Tamil Nadu Power Limited
    "NU": "NUPPL",   # NLC Upper Stage Power Projects
    "NR": "NIRL",    # Neyveli Infrastructure Resources Limited
    "NG": "NIGEL"    # Neyveli Green Energy Limited
}

PROJECT_TYPES = {
    "S": "Service", "I": "Income", "N": "Non-Plan",
    "C": "Capex", "E": "Excetra", "F": "Feasibility",
    "R": "R&D", "O": "Opex", "M": "Material"
}
```

Project IDs follow the pattern: `[Company:2][Type:1][Sequence]`
Example: `NL-C-001` = NLCIL Capex project 001

## Required External Files

- **WBS_NAMES.XLSX**: Master reference file containing WBS element descriptions (required in same directory as input files)
- **nlcil.png**: Application icon (located at `../Data/nlcil.png`)

## File-Specific Notes

### BudgetReport.py vs BudgetUpdates.py

These appear similar but have key differences:

**BudgetReport.py**:
- Cleaning pattern: removes lines `[0, 1, 4, last]` from DAT file
- Standard WBS processing

**BudgetUpdates.py**:
- Cleaning pattern: removes lines `[0, 3, last]`
- Enhanced regex-based child element detection with `fullmatch`
- Asterisk replacement for cleaner presentation

### BudgetVariance.py

Unique input/processing:
- Processes HTML files (not DAT files)
- Uses `pd.read_html()` for table extraction
- Removes first two HTML lines before processing
- Highlights summary WBS in orange (others use light green)
- Header cleanup: strips trailing '1' characters from column names

### GlimpsOfProjects.py

Advanced interactive dashboard features:
- Cross-tabulation with `pd.crosstab()` for statistical analysis
- 3D bar charts with gradient effects
- Data validation dropdowns for interactive filtering
- INDEX-MATCH Excel formulas for real-time updates: `=INDEX($B$2:$F$7, ROW()-10, MATCH($A$10, $B$1:$F$1, 0))`
- Project ID regex extraction: `r"PRJ\s+([A-Z0-9-]+)"`

### YearEnd558.py

Multi-dimensional data slicing:
- Uses `pd.IndexSlice` for multi-level column processing
- Extracts "Available" vs "Assigned" dimensions into separate sheets
- Workbook-level style registration for performance
- Pattern: `df.loc[:, pd.IndexSlice[:, 'Available']]`

## Coding Patterns

### Module Execution Pattern

All report modules follow this structure:

```python
def main():
    try:
        # 1. File selection
        file_path, file_name = FileHandler.get_file_path_and_name()
        if not file_path:
            return

        # 2. Data processing
        processor = DataProcessor(file_path, file_name)
        processor.clean_data(output_file)
        processor.transform_data(master_file, output_file, cleaned_file)

        # 3. Excel formatting
        formatter = ExcelFormatter(output_file)
        formatter.apply_all_formatting()
        formatter.save()

        print(f"Successfully generated: {output_file}")

    except Exception as e:
        print(f"Error: {str(e)}")
        # Error dialogs handled by error_handler.py

if __name__ == "__main__":
    app = QApplication.instance() or QApplication(sys.argv)
    main()
```

### Error Handling

The `@handle_error` decorator (from `error_handler.py`) provides:
- Automatic logging to `logs/sap_reports_YYYYMMDD.log`
- User-friendly error dialogs via QMessageBox
- Exception classification (FileProcessingError, DataValidationError, ExcelGenerationError)
- Full stack traces in log files

### Excel Formatting Standards

Consistent formatting applied across all reports:
- **Font**: Bookman Old Style, 12pt
- **Currency Format**: `₹ #,##0.00;[Red]₹ -#,##0.00` (Indian Rupee with red negatives)
- **Headers**: Yellow background (`FFFF00`), bold, black borders
- **Rows**: Alternating sky blue (`87CEEB`) and white
- **Summary WBS**: Light green (`90EE90`) or orange (`FFA500`) highlighting
- **Tables**: TableStyleMedium9 with filter dropdowns
- **Freeze Panes**: Typically at `E3` or `D3`

### Master Data Integration

WBS descriptions are mapped using `WBS_NAMES.XLSX`:

```python
# Standard pattern across modules
master_df = pd.read_excel('WBS_NAMES.XLSX')
mapping_dict = master_df.set_index('WBS_element')['Name'].to_dict()
df['Description'] = df['WBS_element'].map(mapping_dict)
```

## Common Pitfalls

1. **Encoding Issues**: SAP DAT files use `ISO-8859-1` encoding, not UTF-8
2. **Multi-Level Headers**: DAT files have headers in rows 0 and 1, requiring `header=[0, 1]`
3. **Column Names as Tuples**: Multi-level headers result in tuple column names: `('Budget', 'Total')`
4. **Cleaning Line Numbers**: Different report types remove different metadata lines (see `config.py:CLEANING_PATTERNS`)
5. **WBS Pattern Matching**: Use `re.escape()` before adding regex patterns to handle special characters in WBS IDs
6. **File Dependencies**: Master data file must be in the same directory as input files

## Logging and Debugging

Logs are written to `logs/sap_reports_YYYYMMDD.log` with:
- Timestamp, module name, log level
- Function names and parameters
- Full exception stack traces
- File operations (read, write, processing stages)

Check logs when debugging processing errors or data validation issues.

## Extension Points

To add a new report type:

1. Create new Python file following the FileHandler → DataProcessor → ExcelFormatter pattern
2. Add configuration to `config.py` if needed (cleaning patterns, color schemes, business mappings)
3. Add button to menu files (`menu.py`, `menuPyside.py`, `MenuPySide1.py`)
4. Implement `main()` function that can be called via `run_module()`
5. Use `@handle_error` decorator for automatic error handling
6. Follow existing naming convention: `{ReportType}.py` with PascalCase
