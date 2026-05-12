#!/usr/bin/env python3
"""
Enhanced DAT file processor for Project Analysis Report:

1. Read 558 (Budget) and 532 (Plan) DAT files
   - 558: Remove rows 0, 1, 4, -1 to get 2 header rows
   - 532: Remove rows 0, 3, -1 to get 2 header rows (rows 1 and 2)

2. Both files have same two-level header structure:
   - Primary header: Time periods (Total of years, 2025, 2026, 2027, Balance, etc.)
   - Sub-header: Metrics (Budget, Actual, Plan, Commitment, Available, etc.)

3. Parse ProjectID and ProjectName from Object column using regex
   - 558 format: "6* ProjectName PRJ ProjectID"
   - 532 format: "6* PRJ ProjectID ProjectName"

4. Merge by time periods:
   - For each time period, position Plan (from 532) before Budget columns (from 558)
   - This creates aligned columns: Total_Plan, Total_Budget, Total_Actual, etc.

5. Inner join on ProjectID and replace NaN with 0

This merged dataset serves as the primary source for Project Analysis:
- Plan vs Budget
- Budget vs Actual
- Budget vs Commitment
- Budget vs Remaining (Available)
"""
import re
import pandas as pd
import numpy as np


def clean_dat_file(file_path, report_type='558'):
    """
    Read DAT file and remove specific rows based on report type

    558: Remove rows 0, 1, 4, and -1 (last row) - leaves 2 header rows
    532: Remove rows 0, 3, and -1 (last row) - leaves 2 header rows (1, 2)

    Returns remaining lines
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Total lines read from {file_path}: {len(lines)}")

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

    print(f"Remaining lines after cleanup: {len(lines)}")
    print(f"Rows deleted: {rows_to_delete}\n")
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

    print(f"Primary headers count: {len(primary_headers)}")
    print(f"Sub-headers count: {len(sub_headers)}")

    # Ensure both have same length by padding the shorter one
    max_len = max(len(primary_headers), len(sub_headers))
    while len(primary_headers) < max_len:
        primary_headers.append('')
    while len(sub_headers) < max_len:
        sub_headers.append('')

    print(f"After padding - Primary: {len(primary_headers)}, Sub: {len(sub_headers)}")

    # Find 'Object' column - it can be in either primary or sub-headers
    object_idx = None
    object_in_primary = False

    if 'Object' in sub_headers:
        object_idx = sub_headers.index('Object')
        object_in_primary = False
        print(f"'Object' column found in sub-headers at index: {object_idx}")
    elif 'Object' in primary_headers:
        object_idx = primary_headers.index('Object')
        object_in_primary = True
        print(f"'Object' column found in primary-headers at index: {object_idx}")

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
        level = m.group(1).strip()
        project_name = m.group(2).strip()
        wbs_type = m.group(3).strip()
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
        level = m.group(1).strip()
        wbs_type = m.group(2).strip()
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
    print(f"\n{'='*80}")
    print(f"Processing {report_type} Report: {file_path}")
    print(f"{'='*80}\n")

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

    print(f"Data rows extracted: {len(data_rows)}")

    # Step 4: Update headers (replace 'Object' with 'ProjectID' and 'ProjectName')
    if object_idx is not None:
        if object_in_primary:
            # Object is in primary headers (532 case)
            # Replace 'Object' in primary_headers with 'Project Info' (duplicate for both columns)
            primary_headers.pop(object_idx)
            primary_headers.insert(object_idx, 'Project Info')
            primary_headers.insert(object_idx, 'Project Info')

            # Replace corresponding sub_header with 'ProjectID' and 'ProjectName'
            sub_headers.pop(object_idx)
            sub_headers.insert(object_idx, 'ProjectName')
            sub_headers.insert(object_idx, 'ProjectID')
        else:
            # Object is in sub-headers (558 case)
            # Update sub-headers
            sub_headers.pop(object_idx)
            sub_headers.insert(object_idx, 'ProjectName')
            sub_headers.insert(object_idx, 'ProjectID')

            # Update primary headers (duplicate the primary header for both new columns)
            primary_header_at_object = primary_headers[object_idx]
            primary_headers.pop(object_idx)
            primary_headers.insert(object_idx, primary_header_at_object)
            primary_headers.insert(object_idx, primary_header_at_object)

    print(f"After header update - Primary: {len(primary_headers)}, Sub: {len(sub_headers)}")

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
        print(f"WARNING: DataFrame has {len(df.columns)} columns but headers have {len(sub_headers)}")
        # Adjust DataFrame columns to match headers
        if len(df.columns) < len(sub_headers):
            # Add empty columns
            for i in range(len(sub_headers) - len(df.columns)):
                df[len(df.columns)] = ''
        elif len(df.columns) > len(sub_headers):
            # Trim extra columns
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

    print(f"DataFrame shape: {df.shape}")
    print(f"DataFrame columns (first 5): {list(df.columns[:5])}\n")

    return df


def merge_reports(df_558, df_532):
    """
    Merge 558 and 532 reports by time periods
    - For each time period (Total of years, 2025, 2026, etc.):
      - Add Plan column from 532 before Budget columns from 558
    - This creates a meaningful dataset for Plan vs Budget analysis

    Args:
        df_558: DataFrame from 558 report (Budget/Actual/Commitment data)
        df_532: DataFrame from 532 report (Plan/Actual/Variance data)

    Returns:
        Merged DataFrame with Plan and Budget data organized by time period
    """
    print(f"\n{'='*80}")
    print(f"Merging 558 (Budget) and 532 (Plan) Reports by Time Periods")
    print(f"{'='*80}\n")

    # Find ProjectID columns in both DataFrames (before any processing)
    project_id_col_558 = None
    project_name_col_558 = None
    project_id_col_532 = None
    project_name_col_532 = None

    for col in df_558.columns:
        if col[1] == 'ProjectID':
            project_id_col_558 = col
        elif col[1] == 'ProjectName':
            project_name_col_558 = col

    for col in df_532.columns:
        if col[1] == 'ProjectID':
            project_id_col_532 = col
        elif col[1] == 'ProjectName':
            project_name_col_532 = col

    if project_id_col_558 is None or project_id_col_532 is None:
        raise ValueError("ProjectID column not found in one or both DataFrames")

    print(f"558 DataFrame - Rows: {len(df_558)}, Columns: {len(df_558.columns)}")
    print(f"532 DataFrame - Rows: {len(df_532)}, Columns: {len(df_532.columns)}")

    # Group columns by time period (primary header)
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

    print(f"\nTime periods found:")
    print(f"  558 time periods: {len(time_periods_558)}")
    print(f"  532 time periods: {len(time_periods_532)}")
    print(f"  Common time periods: {len(common_periods)}")
    print(f"\nCommon periods: {common_periods}")

    # Create temporary single-level column names for merging
    # We'll restore the multi-level structure after merge
    df_558_temp = df_558.copy()
    df_532_temp = df_532.copy()

    # Flatten column names temporarily with format "Period|Metric"
    df_558_temp.columns = ['|'.join(map(str, col)) for col in df_558_temp.columns]
    df_532_temp.columns = ['|'.join(map(str, col)) for col in df_532_temp.columns]

    project_id_558_flat = '|'.join(map(str, project_id_col_558))
    project_id_532_flat = '|'.join(map(str, project_id_col_532))

    print(f"\nFlattened ProjectID columns for merge:")
    print(f"  558: {project_id_558_flat}")
    print(f"  532: {project_id_532_flat}")

    # Perform inner join on ProjectID
    merged_df = pd.merge(
        df_558_temp,
        df_532_temp,
        left_on=project_id_558_flat,
        right_on=project_id_532_flat,
        how='inner',
        suffixes=('_558', '_532')
    )

    print(f"\nAfter join: {len(merged_df)} rows, {len(merged_df.columns)} columns")

    # Now select and reorder columns - working with flattened names
    final_columns = []
    project_name_558_flat = '|'.join(map(str, project_name_col_558))

    # Add ProjectID and ProjectName (use from 558)
    final_columns.append(project_id_558_flat)

    # The merge might have added a suffix to ProjectName, so check for it
    if project_name_558_flat in merged_df.columns:
        final_columns.append(project_name_558_flat)
    elif f"{project_name_558_flat}_558" in merged_df.columns:
        final_columns.append(f"{project_name_558_flat}_558")
    else:
        print(f"\nWarning: ProjectName column not found in merged dataframe")

    # For each time period, add Plan from 532 then other columns from 558
    for period in common_periods:
        # Skip empty period
        if not period:
            continue

        # Add Plan column from 532 for this period
        plan_col_532 = f"{period}|Plan"
        if plan_col_532 in merged_df.columns:
            final_columns.append(plan_col_532)

        # Add all other columns from 558 for this period (except ProjectID/ProjectName)
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
        parts = col.split('|', 1)  # Split on first | only
        if len(parts) == 2:
            # Remove _558 and _532 suffixes from column names
            metric = parts[1].replace('_558', '').replace('_532', '')
            multi_level_cols.append((parts[0], metric))
        else:
            multi_level_cols.append(('', parts[0]))

    merged_df.columns = pd.MultiIndex.from_tuples(multi_level_cols)

    print(f"\nFinal DataFrame shape: {merged_df.shape}")
    print(f"\nFirst 20 columns (multi-level):")
    for i, col in enumerate(merged_df.columns[:20]):
        print(f"  {i+1:2d}. Period: '{col[0]:25s}' | Metric: '{col[1]}'")

    # Replace all NaN values with 0
    merged_df = merged_df.fillna(0)

    print(f"\nNaN values replaced with 0")

    return merged_df


def main():
    """
    Main execution function
    """
    # File paths
    file_558 = r"D:\New-PS-Reports\PS-Reports\Data\ALL_PROJECT_558.DAT"
    file_532 = r"D:\New-PS-Reports\PS-Reports\Data\ALL_PROJECT_532.DAT"

    # Process both files
    df_558 = process_dat_file(file_558, report_type='558')
    df_532 = process_dat_file(file_532, report_type='532')

    # Merge the reports
    merged_df = merge_reports(df_558, df_532)

    # Display results
    print(f"\n{'='*80}")
    print(f"FINAL RESULTS - Project Analysis Dataset")
    print(f"{'='*80}\n")

    print("Multi-Level Column Structure (first 20 columns):")
    for i, col in enumerate(merged_df.columns[:20]):
        print(f"  {i+1:2d}. Period: '{col[0]:25s}' | Metric: '{col[1]}'")

    print(f"\nDataFrame Info:")
    print(f"  Total Rows: {len(merged_df)}")
    print(f"  Total Columns: {len(merged_df.columns)}")
    print(f"  Memory Usage: {merged_df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")

    print(f"\nFirst 3 projects (showing structure):")
    print(merged_df.head(3))

    # Save to Excel with multi-level headers
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = rf"D:\New-PS-Reports\PS-Reports\Output\project_analysis_{timestamp}.xlsx"
    try:
        # Create Excel writer with xlsxwriter engine for better formatting
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            # Convert to DataFrame with regular columns for Excel export
            # Flatten the multi-index columns for export
            export_df = merged_df.copy()

            workbook = writer.book
            worksheet = workbook.add_worksheet('Project Analysis')

            # Format for headers
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'align': 'center',
                'bg_color': '#4472C4',
                'font_color': 'white',
                'border': 1
            })

            # Format for data
            data_format = workbook.add_format({
                'border': 1,
                'num_format': '#,##0.00'
            })

            # Write multi-level headers (row 0 and row 1)
            for col_num, col in enumerate(export_df.columns):
                worksheet.write(0, col_num, col[0], header_format)  # Time period
                worksheet.write(1, col_num, col[1], header_format)  # Metric
                # Set column width
                worksheet.set_column(col_num, col_num, 15)

            # Write data starting from row 2
            for row_num, row_data in enumerate(export_df.values, start=2):
                for col_num, value in enumerate(row_data):
                    if isinstance(value, (int, float)):
                        worksheet.write_number(row_num, col_num, value, data_format)
                    else:
                        worksheet.write(row_num, col_num, value, data_format)

        print(f"\nProject Analysis dataset saved to: {output_path}")
        print(f"\nThis dataset can now be used for:")
        print(f"  - Plan vs Budget analysis")
        print(f"  - Budget vs Actual analysis")
        print(f"  - Budget vs Commitment analysis")
        print(f"  - Budget vs Remaining (Available) analysis")
    except Exception as e:
        print(f"\nWarning: Could not save to Excel: {e}")

    return merged_df


if __name__ == "__main__":
    result_df = main()
