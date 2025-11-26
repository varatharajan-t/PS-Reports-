# WBS Error Handling - Implementation Summary

## Overview

Comprehensive error handling has been implemented for missing or unavailable WBS master data (WBS_NAMES.XLSX). The system now gracefully handles scenarios where WBS data is not available, providing clear warnings and continuing to function without crashing.

---

## What Was Implemented

### 1. **Enhanced MasterDataManager** (`reports/services/data_processing.py`)

#### New Method: `check_wbs_data_availability()`
```python
def check_wbs_data_availability(self) -> tuple[bool, str]:
    """
    Check if WBS master data is available in the database.
    Returns: (is_available: bool, message: str)
    """
```

**Features:**
- ✅ Checks if WBS data exists in database
- ✅ Checks if WBS_NAMES.XLSX file exists on disk
- ✅ Provides detailed error messages for both scenarios
- ✅ Caches the check result to avoid repeated database queries
- ✅ Logs warnings when data is missing

#### Updated Method: `map_wbs_descriptions()`
**Previous Behavior:**
- Would silently fail if no WBS data
- No user notification

**New Behavior:**
- ✅ Checks data availability first
- ✅ Logs detailed warnings if data missing
- ✅ **Continues processing** without crashing
- ✅ Returns DataFrame unchanged if no WBS data
- ✅ Reports mapping statistics (mapped vs unmapped)

---

### 2. **Global Warning Banner** (`reports/context_processors.py`)

Created two context processors that add data to ALL templates:

#### `wbs_data_status(request)`
**Provides:**
- `wbs_data_available`: Boolean flag
- `wbs_element_count`: Number of WBS elements in database
- `wbs_warning`: Dictionary with warning details (if data missing)

**Warning Types:**
1. **File exists but not imported** → Yellow warning
   - Shows: "Run `python manage.py import_master_data`"
2. **File missing** → Red danger alert
   - Shows: "Add WBS_NAMES.XLSX file first"

#### `system_status(request)`
**Provides:**
- Company codes count
- Project types count
- WBS elements count

---

### 3. **Visual Warning Banner** (`reports/templates/base.html`)

Added dismissible alert banner that appears on **all pages** when WBS data is missing:

```html
{% if wbs_warning %}
    <div class="alert alert-{{ wbs_warning.type }}">
        <h5>WBS Master Data Missing</h5>
        <p>{{ wbs_warning.message }}</p>
        <hr>
        <p><strong>Impact:</strong> Reports will be generated without WBS descriptions.</p>
    </div>
{% endif %}
```

**Features:**
- ✅ Dismissible (users can close it)
- ✅ Color-coded (yellow warning or red danger)
- ✅ Shows exact command to run
- ✅ Explains the impact on reports
- ✅ Displays on every page until resolved

---

### 4. **WBS Status Check Command** (`check_wbs_data`)

Created a comprehensive diagnostic management command:

```bash
python manage.py check_wbs_data
```

**Output Includes:**
- 📁 **File Status**: Location and size of WBS_NAMES.XLSX
- 📊 **Database Status**: Count of WBS elements, company codes, project types
- 💡 **Recommendations**: Specific actions to take
- 📈 **Impact Assessment**: How missing data affects reports
- ✅/⚠️/❌ **Status Indicators**: Visual feedback on system health

**Sample Output:**
```
======================================================================
WBS Master Data Status Check
======================================================================

📁 WBS File Location: data/WBS_NAMES.XLSX
   ✓ File exists (4.72 KB)

📊 Database Status:
   ✗ WBS Elements: 0 records (not loaded)
   ✓ Company Codes: 5 records
   ✓ Project Types: 9 records

💡 Recommendations:
   → Run: python manage.py import_master_data

📈 Impact on Reports:
   ⚠ Reports will only show WBS codes (no descriptions)

======================================================================
```

---

## How It Works - End-to-End

### Scenario 1: WBS File Missing

1. **User uploads SAP data and generates report**
2. **MasterDataManager checks for WBS data**
3. **Database is empty (0 WBS elements)**
4. **System checks if file exists** → ❌ Not found
5. **Logs warning**: "WBS file not found at data/WBS_NAMES.XLSX"
6. **Report continues processing** without WBS mapping
7. **User sees banner**: "WBS master data file not found..."
8. **Report generated** with WBS codes but no descriptions

### Scenario 2: WBS File Exists But Not Imported

1. **User uploads SAP data and generates report**
2. **MasterDataManager checks for WBS data**
3. **Database is empty (0 WBS elements)**
4. **System checks if file exists** → ✅ Found
5. **Logs warning**: "File exists. Run import_master_data command"
6. **Report continues processing** without WBS mapping
7. **User sees banner**: "Run `python manage.py import_master_data`"
8. **Report generated** with WBS codes but no descriptions

### Scenario 3: WBS Data Available

1. **User uploads SAP data and generates report**
2. **MasterDataManager checks for WBS data**
3. **Database has WBS elements** → ✅ Available
4. **Logs info**: "WBS master data available: N elements"
5. **Maps WBS descriptions** to codes
6. **Logs statistics**: "X mapped, Y unmapped"
7. **No warning banner shown**
8. **Report generated** with full WBS descriptions

---

## Benefits

### For Users
- ✅ **No crashes** when WBS data missing
- ✅ **Clear warnings** explaining the issue
- ✅ **Actionable steps** to resolve
- ✅ **Reports still work** (with reduced detail)
- ✅ **Visual feedback** on every page

### For Developers
- ✅ **Detailed logging** for troubleshooting
- ✅ **Easy diagnostics** with check command
- ✅ **Graceful degradation** of functionality
- ✅ **No silent failures**
- ✅ **Comprehensive error messages**

### For System Admins
- ✅ **Health check command** for monitoring
- ✅ **Clear remediation steps**
- ✅ **File validation** before import
- ✅ **Database statistics**

---

## Files Created/Modified

### New Files (2)
1. **`reports/context_processors.py`** (65 lines)
   - Global template context for WBS status
   - System statistics provider

2. **`reports/management/commands/check_wbs_data.py`** (145 lines)
   - Diagnostic command for WBS data
   - Comprehensive status reporting

### Modified Files (3)
1. **`reports/services/data_processing.py`**
   - Enhanced `MasterDataManager` class
   - Added `check_wbs_data_availability()` method
   - Improved `map_wbs_descriptions()` with error handling

2. **`django_project/settings.py`**
   - Added context processors to TEMPLATES
   - Integrated WBS status checking globally

3. **`reports/templates/base.html`**
   - Added WBS warning banner
   - Displays on all pages when data missing

---

## Testing the Implementation

### 1. Check Current Status
```bash
python manage.py check_wbs_data
```

### 2. Test Without WBS Data
```bash
# Temporarily rename the file (if it exists)
mv data/WBS_NAMES.XLSX data/WBS_NAMES.XLSX.backup

# Visit any page - you'll see a RED warning banner
# Generate a report - it works but without descriptions

# Check status
python manage.py check_wbs_data
```

### 3. Test With File But No Import
```bash
# Restore file
mv data/WBS_NAMES.XLSX.backup data/WBS_NAMES.XLSX

# Clear database (optional)
# Visit any page - you'll see a YELLOW warning banner
# Check status
python manage.py check_wbs_data
```

### 4. Import and Test
```bash
# Import the data
python manage.py import_master_data

# Check status
python manage.py check_wbs_data

# Visit any page - NO warning banner!
# Generate reports - full WBS descriptions included
```

---

## Command Reference

### Check WBS Status
```bash
python manage.py check_wbs_data
```
Shows comprehensive status of WBS master data.

### Import Master Data
```bash
python manage.py import_master_data
```
Imports Company Codes, Project Types, and WBS Elements from settings and file.

### View WBS Data in Admin
```
http://localhost:8000/admin/reports/wbselement/
```
Browse and search imported WBS elements.

---

## Error Scenarios Handled

| Scenario | Detection | User Notification | System Behavior |
|----------|-----------|-------------------|-----------------|
| File missing, DB empty | ✅ | Red banner + logs | Continue without mapping |
| File exists, DB empty | ✅ | Yellow banner + logs | Continue without mapping |
| File missing, DB has data | ✅ | None (uses DB) | Normal operation |
| File exists, DB has data | ✅ | None | Normal operation |
| File corrupt/unreadable | ✅ | Error during import | Import fails safely |
| Partial WBS mapping | ✅ | Logs unmapped count | Reports show partial data |

---

## Performance Impact

- **Negligible**: WBS check is cached per MasterDataManager instance
- **Context processor**: Runs once per request, results cached
- **Database query**: Single COUNT query per request
- **No impact on report generation**: Mapping happens in memory

---

## Future Enhancements (Optional)

1. **Admin Action**: Add "Check WBS Status" button in admin interface
2. **Scheduled Checks**: Celery task to monitor WBS data daily
3. **Email Alerts**: Notify admins when WBS data missing
4. **Auto-import**: Automatically import when file detected
5. **Version Tracking**: Track when WBS file was last updated

---

## Conclusion

The WBS error handling implementation provides:
- ✅ **Robust error detection** at multiple levels
- ✅ **User-friendly warnings** with actionable steps
- ✅ **Graceful degradation** when data unavailable
- ✅ **Comprehensive diagnostics** for troubleshooting
- ✅ **Production-ready** error management

Reports will **never crash** due to missing WBS data, and users always know exactly what to do to resolve the issue.

---

**Implementation Date**: November 26, 2025
**Status**: ✅ Complete and Tested
**Severity**: All error scenarios handled gracefully
