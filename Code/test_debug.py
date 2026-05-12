#!/usr/bin/env python3
"""
Debug script to examine 532 and 558 file structures
"""
import re
import pandas as pd

def clean_dat_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    rows_to_delete = [0, 1, 4, -1]
    actual_indices = []
    for idx in rows_to_delete:
        if idx == -1:
            actual_indices.append(len(lines) - 1)
        else:
            actual_indices.append(idx)

    actual_indices.sort(reverse=True)
    for idx in actual_indices:
        if 0 <= idx < len(lines):
            del lines[idx]

    return lines

def extract_headers(lines):
    if len(lines) < 2:
        raise ValueError("Insufficient lines for header extraction")

    primary_headers = lines[0].strip().split('\t')
    sub_headers = lines[1].strip().split('\t')

    max_len = max(len(primary_headers), len(sub_headers))
    while len(primary_headers) < max_len:
        primary_headers.append('')
    while len(sub_headers) < max_len:
        sub_headers.append('')

    return primary_headers, sub_headers

# Check 532 file structure
file_532 = r"D:\New-PS-Reports\PS-Reports\Data\ALL_PROJECT_532.DAT"
lines_532 = clean_dat_file(file_532)
primary_532, sub_532 = extract_headers(lines_532)

print("="*80)
print("532 FILE STRUCTURE")
print("="*80)
print(f"\nTotal columns: {len(primary_532)}")
print(f"\nColumn structure (Primary | Sub-header):")
for i, (p, s) in enumerate(zip(primary_532, sub_532)):
    print(f"{i:2d}. '{p}' | '{s}'")

# Check 558 file structure
file_558 = r"D:\New-PS-Reports\PS-Reports\Data\ALL_PROJECT_558.DAT"
lines_558 = clean_dat_file(file_558)
primary_558, sub_558 = extract_headers(lines_558)

print("\n" + "="*80)
print("558 FILE STRUCTURE")
print("="*80)
print(f"\nTotal columns: {len(primary_558)}")
print(f"\nColumn structure (Primary | Sub-header):")
for i, (p, s) in enumerate(zip(primary_558[:15], sub_558[:15])):  # Show first 15
    print(f"{i:2d}. '{p}' | '{s}'")
print("... (showing first 15 columns only)")
