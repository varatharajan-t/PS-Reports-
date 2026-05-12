import re

text = "NL-N-MN1-001"

# Regular expression pattern to capture the four parts
pattern = r"^(\w{2})-(\w)-(\w{3})-(\d{3})$"

match = re.match(pattern, text)

if match:
    company_code = match.group(1)
    project_type = match.group(2)
    plant = match.group(3)
    serial_number = match.group(4)

    print("Company Code:", company_code)
    print("Project Type:", project_type)
    print("Plant:", plant)
    print("Serial Number:", serial_number)
else:
    print("The format does not match.")
