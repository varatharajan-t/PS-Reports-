# Project Analysis Report - Updated Implementation

## Overview
The Project Analysis report has been completely rewritten to use the logic from `test.py`, providing comprehensive year-on-year analysis of projects based on 558 and 532 SAP reports.

## Key Changes

### 1. **Report Processing Logic**
- **558 Report (Budget data)**: Removes rows 0, 1, 4, -1 to get proper 2-level headers
- **532 Report (Plan data)**: Removes rows 0, 3, -1 to get proper 2-level headers
- Both reports now have aligned time period structures

### 2. **Time Period Alignment**
Both reports share the same header structure:
- **Primary headers**: Time periods (Total of years, 2025, 2026, 2027, 2028 and Following, Previous years, Overall values)
- **Sub-headers**: Metrics (Plan, Budget, Actual, Commitment, Available, Assigned, Variance, Var %)

### 3. **Data Merging**
- Inner join on ProjectID
- For each time period:
  - **Plan** column (from 532) is positioned **before** Budget columns (from 558)
  - Example: 2025_Plan → 2025_Budget → 2025_Actual → 2025_Commitment → etc.
- Creates a meaningful dataset for analysis

### 4. **Year-on-Year Analysis**
The report now generates comprehensive year-on-year analysis with:
- **Annual totals** for each metric (Plan, Budget, Actual, Commitment, Available)
- **Plan vs Budget variance** calculations (amount and %)
- **Budget vs Actual variance** calculations (amount and %)
- Easy comparison across years (2025, 2026, 2027, etc.)

## Excel Output Structure

The generated Excel file contains **3 sheets**:

### Sheet 1: Project Details
- All projects with complete data by time periods
- Multi-level headers (Time Period | Metric)
- Plan data positioned before Budget data for each period
- Formatted with borders and professional styling

### Sheet 2: Year-on-Year Analysis
- Aggregated totals by year/period
- Columns: Period, Plan, Budget, Actual, Commitment, Available, Assigned, Variance, Var %
- Calculated variance columns:
  - Plan_vs_Budget_Variance
  - Plan_vs_Budget_Variance_%
  - Budget_vs_Actual_Variance
  - Budget_vs_Actual_Variance_%

### Sheet 3: Overall Summary
- Grand totals across all periods
- Metrics:
  - Total Projects
  - Total Plan
  - Total Budget
  - Total Actual
  - Total Commitment
  - Total Available

## How to Use

### 1. Access the Report Interface
Navigate to: `http://127.0.0.1:8000/report/project-analysis/`

### 2. Upload Files
- **558 Report**: Select your Budget file (contains Budget/Actual/Commitment data)
- **532 Report**: Select your Plan file (contains Plan/Variance data)

### 3. Generate Report
Click "Generate Project Analysis Report" button

### 4. Review Results
- View **Year-on-Year Analysis** table directly in the browser
- Download the comprehensive Excel file with all 3 sheets
- See statistics:
  - Total Projects processed
  - Budget Projects count
  - Actual Projects count

## Analysis Capabilities

With this updated report, you can now analyze:

1. **By Year**: 2025, 2026, 2027, etc.
   - Compare planned vs budgeted amounts
   - Track actual spending vs budget
   - Monitor commitment levels

2. **Overall Totals**:
   - See complete project lifecycle totals
   - Understand total financial exposure

3. **Variances**:
   - Plan vs Budget gaps
   - Budget vs Actual execution
   - Percentage-based variance analysis

4. **Time-based Trends**:
   - Year-over-year budget growth
   - Spending patterns across years
   - Commitment trends

## Technical Details

### File: `reports/services/project_analysis_service.py`
Key functions:
- `clean_dat_file()`: Removes specific rows based on report type
- `process_dat_file()`: Parses DAT file with multi-level headers
- `merge_reports()`: Aligns data by time periods
- `create_year_on_year_analysis()`: Generates YoY analysis
- `generate_project_analysis_report()`: Main function that orchestrates everything

### Updated Files:
1. `reports/services/project_analysis_service.py` - Complete rewrite
2. `reports/templates/reports/report_project_analysis.html` - Updated UI
3. `reports/forms.py` - Updated labels for 558/532 reports

### Views:
No changes to `reports/views.py` - The `project_analysis_report_view()` function continues to work as before, now using the updated service.

## Example Analysis Scenarios

### Scenario 1: 2025 Budget Analysis
From the Year-on-Year sheet, you can see:
- How much was planned for 2025
- Actual budget allocated for 2025
- Variance between plan and budget
- Current actual spending in 2025

### Scenario 2: Multi-Year Comparison
Compare across years:
```
Year   | Plan        | Budget      | Variance    | Variance %
-------|-------------|-------------|-------------|------------
2025   | 1,000,000   | 950,000     | -50,000     | -5%
2026   | 1,200,000   | 1,150,000   | -50,000     | -4.2%
2027   | 1,500,000   | 1,450,000   | -50,000     | -3.3%
```

### Scenario 3: Project-Level Detail
From the Project Details sheet:
- Filter by specific ProjectID
- See all time periods for that project
- Analyze plan vs budget vs actual vs commitment for each period

## Benefits

1. **Accurate Time Period Alignment**: No more mismatched columns between reports
2. **Comprehensive Analysis**: All data in one place with proper organization
3. **Variance Tracking**: Built-in variance calculations for quick insights
4. **Year-on-Year Trends**: Easy to spot patterns and anomalies across years
5. **Professional Formatting**: Multi-level headers and clean Excel output

## Future Enhancements

Potential additions:
- Charts in Excel (bar charts for YoY comparison)
- Conditional formatting for variances exceeding thresholds
- Project-wise analysis sheet (breakdown by project)
- Filtering capabilities in Excel (slicers for time periods)

---

**Last Updated**: December 1, 2025
**Version**: 2.0
**Based on**: test.py logic with Django integration
