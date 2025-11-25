"""
Standalone test for Indian currency formatting
"""
import pandas as pd


def format_indian_currency(value):
    """
    Format a number in Indian currency style with crore, lakh separators.
    Example: 12,34,56,789.00
    """
    if pd.isna(value) or value == '':
        return ''

    try:
        # Convert to float if it's not already
        num = float(value)

        # Handle negative numbers
        is_negative = num < 0
        num = abs(num)

        # Format to 2 decimal places
        num_str = f"{num:.2f}"
        integer_part, decimal_part = num_str.split('.')

        # Apply Indian numbering system
        if len(integer_part) <= 3:
            formatted = integer_part
        else:
            # Last 3 digits
            last_three = integer_part[-3:]
            remaining = integer_part[:-3]

            # Group remaining digits in pairs from right to left
            groups = []
            while remaining:
                groups.append(remaining[-2:])
                remaining = remaining[:-2]

            groups.reverse()
            formatted = ','.join(groups) + ',' + last_three

        result = f"₹ {formatted}.{decimal_part}"

        if is_negative:
            result = f"-{result}"

        return result
    except (ValueError, TypeError):
        return str(value)


# Test cases for Indian currency formatting
test_values = [
    (1234567890.50, "₹ 1,23,45,67,890.50"),      # Crores
    (12345678.75, "₹ 1,23,45,678.75"),            # Lakhs
    (123456.00, "₹ 1,23,456.00"),                 # Lakhs
    (12345.00, "₹ 12,345.00"),                    # Thousands
    (123.45, "₹ 123.45"),                         # Hundreds
    (-50000.00, "-₹ 50,000.00"),                  # Negative
    (0, "₹ 0.00"),                                # Zero
    (5000000, "₹ 50,00,000.00"),                  # 50 Lakhs
]

print("Testing Indian Currency Formatting:\n")
print(f"{'Input':<20} {'Expected':<25} {'Actual':<25} {'Status'}")
print("-" * 90)

all_passed = True
for input_val, expected in test_values:
    actual = format_indian_currency(input_val)
    status = "✓ PASS" if actual == expected else "✗ FAIL"
    if actual != expected:
        all_passed = False
    print(f"{input_val:<20} {expected:<25} {actual:<25} {status}")

print("\n" + "=" * 90)
if all_passed:
    print("✓ All tests passed!")
else:
    print("✗ Some tests failed!")
