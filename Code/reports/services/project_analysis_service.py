"""
Service layer for generating the Project Analysis Report with Year-on-Year Analysis.

This module processes two DAT files:
- 558: Budget/Actual/Commitment data
- 532: Plan/Actual/Variance data

Both files have the same two-level header structure with time periods.
Logic derived from: test.py
"""
import os
import re
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

from django.conf import settings
from .error_handling import handle_error, FileProcessingError

logger = logging.getLogger(__name__)


def clean_dat_file(file_path, report_type='558'):
    """
    Read DAT file and remove specific rows based on report type

    558: Remove rows 0, 1, 4, and -1 (last row) - leaves 2 header rows
    532: Remove rows 0, 3, and -1 (last row) - leaves 2 header rows (1, 2)

    Returns remaining lines
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    logger.info(f"Total lines read from {file_path}: {len(lines)}")

    # Different row deletion strategy based on report type
    if report_type == '532':
        # For 532: Remove rows 0, 3, and -1 to get rows 1 and 2 as headers
        rows_to_delete = [0, 3, -1]
    else:
        # For 558: Remove rows 0, 1, 4, and -1 (default behavior)
        rows_to_delete = [0, 1, 4, -1]

    # Convert -1 to actual index
    actual_indices = []
    for idx in rows_to_delete:
        if idx == -1:
            actual_indices.append(len(lines) - 1)
        else:
            actual_indices.append(idx)

    # Sort in descending order to delete from end to beginning
    actual_indices.sort(reverse=True)

    # Delete the rows
    for idx in actual_indices:
        if 0 <= idx < len(lines):
            del lines[idx]

    logger.info(f"Remaining lines after cleanup: {len(lines)}")
    return lines


def extract_headers(lines):
    """
    Extract primary headers (row 0) and sub-headers (row 1) as lists
    Preserves order of fields
    """
    if len(lines) < 2:
        raise ValueError("Insufficient lines for header extraction")

    # Primary headers (Level 0)
    primary_headers = lines[0].strip().split('\t')

    # Sub-headers (Level 1)
    sub_headers = lines[1].strip().split('\t')

    # Ensure both have same length by padding the shorter one
    max_len = max(len(primary_headers), len(sub_headers))
    while len(primary_headers) < max_len:
        primary_headers.append('')
    while len(sub_headers) < max_len:
        sub_headers.append('')

    # Find 'Object' column - it can be in either primary or sub-headers
    object_idx = None
    object_in_primary = False

    if 'Object' in sub_headers:
        object_idx = sub_headers.index('Object')
        object_in_primary = False
    elif 'Object' in primary_headers:
        object_idx = primary_headers.index('Object')
        object_in_primary = True

    return primary_headers, sub_headers, object_idx, object_in_primary


def parse_558_object(object_str):
    """
    Parse 558 format: 6* ProjectName PRJ ProjectID
    Example: "6* TS2          PRJ 12KST1B"
    """
    pattern = re.compile(r"^(6\*)\s+(.*?)\s+(PRJ)\s+([A-Z0-9-]{12})")
    tempStr = object_str[:42]  # First 42 characters
    m = re.match(pattern, tempStr)

    if m:
        project_name = m.group(2).strip()
        project_id = m.group(4).strip()
        return project_id, project_name
    return None, None


def parse_532_object(object_str):
    """
    Parse 532 format: 6* PRJ ProjectID ProjectName
    Example: "6* PRJ 12KST1B TS2"
    """
    pattern = re.compile(r"^(6\*)\s+(PRJ)\s+([A-Z0-9-]{12})\s+(.*)")
    tempStr = object_str[:55]  # First 55 characters
    m = re.match(pattern, tempStr)

    if m:
        project_id = m.group(3).strip()
        project_name = m.group(4).strip()
        return project_id, project_name
    return None, None


def process_dat_file(file_path, report_type='558'):
    """
    Process DAT file and create DataFrame with multi-level headers

    Args:
        file_path: Path to DAT file
        report_type: '558' or '532' to determine regex pattern and header cleanup

    Returns:
        DataFrame with multi-level column headers
    """
    logger.info(f"Processing {report_type} Report: {file_path}")

    # Step 1: Clean the file with appropriate row deletion for report type
    lines = clean_dat_file(file_path, report_type=report_type)

    # Step 2: Extract headers
    primary_headers, sub_headers, object_idx, object_in_primary = extract_headers(lines)

    # Step 3: Process data rows (skip first 2 lines which are headers)
    data_rows = []
    parse_function = parse_558_object if report_type == '558' else parse_532_object

    for line in lines[2:]:  # Skip header rows
        row_data = line.strip().split('\t')

        # Ensure row has enough columns - pad to match sub_headers length
        while len(row_data) < len(sub_headers):
            row_data.append('')

        # Extract ProjectID and ProjectName from Object column
        if object_idx is not None and object_idx < len(row_data):
            object_str = row_data[object_idx]
            project_id, project_name = parse_function(object_str)

            # Only process rows with valid project data
            if project_id and project_name:
                # Remove the Object column and insert ProjectID and ProjectName
                row_data.pop(object_idx)
                row_data.insert(object_idx, project_name)
                row_data.insert(object_idx, project_id)

                data_rows.append(row_data)

    logger.info(f"Data rows extracted: {len(data_rows)}")

    # Step 4: Update headers (replace 'Object' with 'ProjectID' and 'ProjectName')
    if object_idx is not None:
        if object_in_primary:
            # Object is in primary headers (532 case)
            primary_headers.pop(object_idx)
            primary_headers.insert(object_idx, 'Project Info')
            primary_headers.insert(object_idx, 'Project Info')

            sub_headers.pop(object_idx)
            sub_headers.insert(object_idx, 'ProjectName')
            sub_headers.insert(object_idx, 'ProjectID')
        else:
            # Object is in sub-headers (558 case)
            sub_headers.pop(object_idx)
            sub_headers.insert(object_idx, 'ProjectName')
            sub_headers.insert(object_idx, 'ProjectID')

            primary_header_at_object = primary_headers[object_idx]
            primary_headers.pop(object_idx)
            primary_headers.insert(object_idx, primary_header_at_object)
            primary_headers.insert(object_idx, primary_header_at_object)

    # Ensure both header arrays have the same length
    max_len = max(len(primary_headers), len(sub_headers))
    while len(primary_headers) < max_len:
        primary_headers.append('')
    while len(sub_headers) < max_len:
        sub_headers.append('')

    # Step 5: Create DataFrame with multi-level headers
    df = pd.DataFrame(data_rows)

    # Ensure DataFrame has correct number of columns
    if len(df.columns) != len(sub_headers):
        if len(df.columns) < len(sub_headers):
            for i in range(len(sub_headers) - len(df.columns)):
                df[len(df.columns)] = ''
        elif len(df.columns) > len(sub_headers):
            df = df.iloc[:, :len(sub_headers)]

    # Create multi-level column index
    df.columns = pd.MultiIndex.from_arrays([primary_headers, sub_headers])

    # Step 6: Convert numeric columns to proper types
    for col in df.columns:
        if col[1] not in ['ProjectID', 'ProjectName']:
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except:
                pass

    logger.info(f"DataFrame shape: {df.shape}")
    return df


def merge_reports(df_558, df_532):
    """
    Merge 558 and 532 reports by time periods
    - For each time period, add Plan from 532 before Budget columns from 558
    - This creates a meaningful dataset for Plan vs Budget analysis

    Args:
        df_558: DataFrame from 558 report (Budget/Actual/Commitment data)
        df_532: DataFrame from 532 report (Plan/Actual/Variance data)

    Returns:
        Merged DataFrame with Plan and Budget data organized by time period
    """
    logger.info("Merging 558 (Budget) and 532 (Plan) Reports by Time Periods")

    # Find ProjectID columns in both DataFrames
    project_id_col_558 = None
    project_name_col_558 = None
    project_id_col_532 = None

    for col in df_558.columns:
        if col[1] == 'ProjectID':
            project_id_col_558 = col
        elif col[1] == 'ProjectName':
            project_name_col_558 = col

    for col in df_532.columns:
        if col[1] == 'ProjectID':
            project_id_col_532 = col

    if project_id_col_558 is None or project_id_col_532 is None:
        raise ValueError("ProjectID column not found in one or both DataFrames")

    # Get unique time periods from both reports
    time_periods_558 = set()
    time_periods_532 = set()

    for col in df_558.columns:
        if col[1] not in ['ProjectID', 'ProjectName']:
            time_periods_558.add(col[0])

    for col in df_532.columns:
        if col[1] not in ['ProjectID', 'ProjectName']:
            time_periods_532.add(col[0])

    # Find common time periods
    common_periods = sorted(time_periods_558.intersection(time_periods_532))
    logger.info(f"Common time periods: {common_periods}")

    # Create temporary single-level column names for merging
    df_558_temp = df_558.copy()
    df_532_temp = df_532.copy()

    # Flatten column names temporarily with format "Period|Metric"
    df_558_temp.columns = ['|'.join(map(str, col)) for col in df_558_temp.columns]
    df_532_temp.columns = ['|'.join(map(str, col)) for col in df_532_temp.columns]

    project_id_558_flat = '|'.join(map(str, project_id_col_558))
    project_id_532_flat = '|'.join(map(str, project_id_col_532))

    # Perform inner join on ProjectID
    merged_df = pd.merge(
        df_558_temp,
        df_532_temp,
        left_on=project_id_558_flat,
        right_on=project_id_532_flat,
        how='inner',
        suffixes=('_558', '_532')
    )

    logger.info(f"After join: {len(merged_df)} rows, {len(merged_df.columns)} columns")

    # Reorder columns - working with flattened names
    final_columns = []
    project_name_558_flat = '|'.join(map(str, project_name_col_558))

    # Add ProjectID and ProjectName (use from 558)
    final_columns.append(project_id_558_flat)

    # The merge might have added a suffix to ProjectName
    if project_name_558_flat in merged_df.columns:
        final_columns.append(project_name_558_flat)
    elif f"{project_name_558_flat}_558" in merged_df.columns:
        final_columns.append(f"{project_name_558_flat}_558")

    # For each time period, add Plan from 532 then other columns from 558
    for period in common_periods:
        # Skip empty period
        if not period:
            continue

        # Add Plan column from 532 for this period
        plan_col_532 = f"{period}|Plan"
        if plan_col_532 in merged_df.columns:
            final_columns.append(plan_col_532)

        # Add all other columns from 558 for this period
        for col in merged_df.columns:
            if col.startswith(f"{period}|") and col not in final_columns:
                # Exclude 532 duplicate columns and Plan column we already added
                if not col.endswith('_532') and '|Plan' not in col:
                    final_columns.append(col)

    # Remove duplicates while preserving order
    seen = set()
    unique_final_columns = []
    for col in final_columns:
        if col not in seen and col in merged_df.columns:
            seen.add(col)
            unique_final_columns.append(col)

    # Select only the columns we want
    merged_df = merged_df[unique_final_columns]

    # Restore multi-level column structure and clean up suffixes
    multi_level_cols = []
    for col in merged_df.columns:
        parts = col.split('|', 1)
        if len(parts) == 2:
            # Remove _558 and _532 suffixes from column names
            metric = parts[1].replace('_558', '').replace('_532', '')
            multi_level_cols.append((parts[0], metric))
        else:
            multi_level_cols.append(('', parts[0]))

    merged_df.columns = pd.MultiIndex.from_tuples(multi_level_cols)

    # Replace all NaN values with 0
    merged_df = merged_df.fillna(0)

    logger.info(f"Final merged DataFrame shape: {merged_df.shape}")
    return merged_df, common_periods


def create_year_on_year_analysis(df_merged, time_periods):
    """
    Create year-on-year analysis DataFrame

    Args:
        df_merged: Merged DataFrame with multi-level columns
        time_periods: List of time periods (years)

    Returns:
        DataFrame with year-on-year analysis
    """
    logger.info("Creating year-on-year analysis")

    # Filter for year periods (2025, 2026, 2027, etc.)
    year_periods = [p for p in time_periods if p.isdigit() or any(year in p for year in ['2025', '2026', '2027', '2028'])]

    analysis_data = []

    for period in year_periods:
        period_data = {'Period': period}

        # Get columns for this period
        period_cols = [col for col in df_merged.columns if col[0] == period]

        # Calculate totals for each metric
        for col in period_cols:
            metric = col[1]
            total = df_merged[col].sum()
            period_data[metric] = total

        analysis_data.append(period_data)

    df_analysis = pd.DataFrame(analysis_data)

    # Calculate variances if columns exist
    if 'Plan' in df_analysis.columns and 'Budget' in df_analysis.columns:
        df_analysis['Plan_vs_Budget_Variance'] = df_analysis['Budget'] - df_analysis['Plan']
        df_analysis['Plan_vs_Budget_Variance_%'] = (
            (df_analysis['Plan_vs_Budget_Variance'] / df_analysis['Plan']) * 100
        ).replace([np.inf, -np.inf], 0)

    if 'Budget' in df_analysis.columns and 'Actual' in df_analysis.columns:
        df_analysis['Budget_vs_Actual_Variance'] = df_analysis['Actual'] - df_analysis['Budget']
        df_analysis['Budget_vs_Actual_Variance_%'] = (
            (df_analysis['Budget_vs_Actual_Variance'] / df_analysis['Budget']) * 100
        ).replace([np.inf, -np.inf], 0)

    return df_analysis


def prepare_chart_data(yoy_analysis, merged_df):
    """
    Prepare data for charts in a format suitable for Chart.js

    Args:
        yoy_analysis: Year-on-Year analysis DataFrame
        merged_df: Merged DataFrame with all project details

    Returns:
        Dictionary with chart data for various visualizations
    """
    import json

    # Convert values to regular Python types for JSON serialization
    def safe_convert(val):
        if pd.isna(val):
            return 0
        if isinstance(val, (np.integer, np.floating)):
            return float(val)
        return val

    chart_data = {}

    # 1. Year-on-Year Comparison Data (Plan vs Budget vs Actual)
    if not yoy_analysis.empty:
        chart_data['yoy_comparison'] = {
            'labels': [str(p) for p in yoy_analysis['Period'].tolist()],
            'datasets': []
        }

        # Add datasets for each metric
        metrics = [
            ('Plan', '#4472C4', 'Plan'),
            ('Budget', '#ED7D31', 'Budget'),
            ('Actual', '#70AD47', 'Actual'),
            ('Commitment', '#FFC000', 'Commitment')
        ]

        for metric, color, label in metrics:
            if metric in yoy_analysis.columns:
                chart_data['yoy_comparison']['datasets'].append({
                    'label': label,
                    'data': [safe_convert(v) for v in yoy_analysis[metric].tolist()],
                    'backgroundColor': color,
                    'borderColor': color,
                    'borderWidth': 2
                })

    # 2. Variance Analysis Data
    if not yoy_analysis.empty:
        variance_labels = []
        plan_vs_budget_data = []
        budget_vs_actual_data = []

        for _, row in yoy_analysis.iterrows():
            variance_labels.append(str(row['Period']))

            if 'Plan_vs_Budget_Variance' in row:
                plan_vs_budget_data.append(safe_convert(row['Plan_vs_Budget_Variance']))

            if 'Budget_vs_Actual_Variance' in row:
                budget_vs_actual_data.append(safe_convert(row['Budget_vs_Actual_Variance']))

        chart_data['variance_analysis'] = {
            'labels': variance_labels,
            'datasets': [
                {
                    'label': 'Plan vs Budget Variance',
                    'data': plan_vs_budget_data,
                    'backgroundColor': '#5B9BD5',
                    'borderColor': '#5B9BD5',
                    'borderWidth': 2
                },
                {
                    'label': 'Budget vs Actual Variance',
                    'data': budget_vs_actual_data,
                    'backgroundColor': '#70AD47',
                    'borderColor': '#70AD47',
                    'borderWidth': 2
                }
            ]
        }

    # 3. Trend Analysis (Line Chart)
    if not yoy_analysis.empty:
        chart_data['trend_analysis'] = {
            'labels': [str(p) for p in yoy_analysis['Period'].tolist()],
            'datasets': []
        }

        trend_metrics = [
            ('Plan', '#4472C4'),
            ('Budget', '#ED7D31'),
            ('Actual', '#70AD47')
        ]

        for metric, color in trend_metrics:
            if metric in yoy_analysis.columns:
                chart_data['trend_analysis']['datasets'].append({
                    'label': metric,
                    'data': [safe_convert(v) for v in yoy_analysis[metric].tolist()],
                    'borderColor': color,
                    'backgroundColor': f"{color}33",  # Add transparency
                    'tension': 0.4,
                    'fill': True
                })

    # 4. Budget Utilization (Donut Chart)
    if not yoy_analysis.empty and 'Budget' in yoy_analysis.columns and 'Actual' in yoy_analysis.columns:
        total_budget = safe_convert(yoy_analysis['Budget'].sum())
        total_actual = safe_convert(yoy_analysis['Actual'].sum())
        remaining = max(0, total_budget - total_actual)

        chart_data['budget_utilization'] = {
            'labels': ['Spent', 'Remaining'],
            'datasets': [{
                'data': [total_actual, remaining],
                'backgroundColor': ['#70AD47', '#C5C5C5'],
                'borderWidth': 2
            }]
        }

    # 5. KPI Summary
    if not yoy_analysis.empty:
        kpis = {}

        for metric in ['Plan', 'Budget', 'Actual', 'Commitment', 'Available']:
            if metric in yoy_analysis.columns:
                kpis[metric] = {
                    'total': safe_convert(yoy_analysis[metric].sum()),
                    'average': safe_convert(yoy_analysis[metric].mean())
                }

        # Calculate overall variances
        if 'Plan' in kpis and 'Budget' in kpis:
            plan_total = kpis['Plan']['total']
            budget_total = kpis['Budget']['total']
            kpis['plan_vs_budget_variance'] = budget_total - plan_total
            kpis['plan_vs_budget_variance_pct'] = (
                (kpis['plan_vs_budget_variance'] / plan_total * 100) if plan_total != 0 else 0
            )

        if 'Budget' in kpis and 'Actual' in kpis:
            budget_total = kpis['Budget']['total']
            actual_total = kpis['Actual']['total']
            kpis['budget_vs_actual_variance'] = actual_total - budget_total
            kpis['budget_vs_actual_variance_pct'] = (
                (kpis['budget_vs_actual_variance'] / budget_total * 100) if budget_total != 0 else 0
            )

        chart_data['kpis'] = kpis

    return chart_data


@handle_error
def generate_project_analysis_report(budget_file_path: str, plan_file_path: str) -> dict:
    """
    Generate the Project Analysis report with Year-on-Year analysis.

    Args:
        budget_file_path: Path to 558 DAT file (Budget data)
        plan_file_path: Path to 532 DAT file (Plan data)

    Returns:
        Dictionary with file_path, data_html, and analysis results
    """
    try:
        # Validate files exist
        if not Path(budget_file_path).exists():
            raise FileProcessingError(f"Budget file not found: {budget_file_path}", "FILE_NOT_FOUND")
        if not Path(plan_file_path).exists():
            raise FileProcessingError(f"Plan file not found: {plan_file_path}", "FILE_NOT_FOUND")

        # Process both files
        logger.info("Processing 558 (Budget) file...")
        df_558 = process_dat_file(budget_file_path, report_type='558')

        logger.info("Processing 532 (Plan) file...")
        df_532 = process_dat_file(plan_file_path, report_type='532')

        # Merge the reports
        logger.info("Merging reports by time periods...")
        merged_df, time_periods = merge_reports(df_558, df_532)

        # Create year-on-year analysis
        yoy_analysis = create_year_on_year_analysis(merged_df, time_periods)

        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"project_analysis_{timestamp}.xlsx"
        reports_dir = settings.BASE_DIR / 'data' / 'reports'
        reports_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(reports_dir / output_filename)

        # Create Excel writer
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            workbook = writer.book

            # Format definitions
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'align': 'center',
                'bg_color': '#4472C4',
                'font_color': 'white',
                'border': 1
            })

            data_format = workbook.add_format({
                'border': 1,
                'num_format': '#,##0.00'
            })

            # Sheet 1: Detailed Project Data
            worksheet1 = workbook.add_worksheet('Project Details')

            # Write multi-level headers
            for col_num, col in enumerate(merged_df.columns):
                worksheet1.write(0, col_num, col[0], header_format)
                worksheet1.write(1, col_num, col[1], header_format)
                worksheet1.set_column(col_num, col_num, 15)

            # Write data starting from row 2
            for row_num, row_data in enumerate(merged_df.values, start=2):
                for col_num, value in enumerate(row_data):
                    if isinstance(value, (int, float)):
                        worksheet1.write_number(row_num, col_num, value, data_format)
                    else:
                        worksheet1.write(row_num, col_num, value, data_format)

            # Sheet 2: Year-on-Year Analysis
            yoy_analysis.to_excel(writer, sheet_name='Year on Year Analysis', index=False)

            worksheet2 = writer.sheets['Year on Year Analysis']
            for col_num in range(len(yoy_analysis.columns)):
                worksheet2.set_column(col_num, col_num, 18)

            # Sheet 3: Overall Summary
            summary_data = {
                'Metric': ['Total Projects', 'Total Plan', 'Total Budget', 'Total Actual',
                          'Total Commitment', 'Total Available'],
                'Value': [
                    len(merged_df),
                    merged_df[[col for col in merged_df.columns if col[1] == 'Plan']].sum().sum(),
                    merged_df[[col for col in merged_df.columns if col[1] == 'Budget']].sum().sum(),
                    merged_df[[col for col in merged_df.columns if col[1] == 'Actual']].sum().sum(),
                    merged_df[[col for col in merged_df.columns if col[1] == 'Commitment']].sum().sum(),
                    merged_df[[col for col in merged_df.columns if col[1] == 'Available']].sum().sum(),
                ]
            }
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Overall Summary', index=False)

        logger.info(f"Project Analysis report saved: {output_path}")

        # Generate HTML preview (Year-on-Year analysis)
        data_html = yoy_analysis.to_html(
            classes='table table-striped table-bordered table-hover',
            index=False,
            float_format=lambda x: f'{x:,.2f}' if pd.notna(x) else ''
        )

        # Prepare chart data for visualization
        chart_data = prepare_chart_data(yoy_analysis, merged_df)

        return {
            "file_path": output_path,
            "data_html": data_html,
            "rows_processed": len(merged_df),
            "budget_projects": len(df_558),
            "actual_projects": len(df_532),
            "time_periods": time_periods,
            "yoy_summary": yoy_analysis.to_dict('records'),
            "chart_data": chart_data
        }

    except Exception as e:
        logger.error(f"Error generating project analysis report: {str(e)}", exc_info=True)
        raise
