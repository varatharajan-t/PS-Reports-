#!/usr/bin/env python3
"""
Check the actual column structure of the 532 file to understand the multi-level headers
"""
import sys
sys.path.append(r'D:\New-PS-Reports\PS-Reports\Code')
from test import process_dat_file

# Process 532 file
df_532 = process_dat_file(r"D:\New-PS-Reports\PS-Reports\Data\ALL_PROJECT_532.DAT", report_type='532')

print("\n" + "="*80)
print("532 DataFrame Multi-Level Columns (ALL columns):")
print("="*80)
for i, col in enumerate(df_532.columns):
    print(f"{i:2d}. Primary: '{col[0]:20s}' | Sub: '{col[1]}'")

# Filter to Plan columns
plan_cols = [col for col in df_532.columns if col[0] == 'Plan']
print("\n" + "="*80)
print(f"PLAN columns only ({len(plan_cols)} total):")
print("="*80)
for i, col in enumerate(plan_cols):
    print(f"{i:2d}. Primary: '{col[0]}' | Sub: '{col[1]}'")
