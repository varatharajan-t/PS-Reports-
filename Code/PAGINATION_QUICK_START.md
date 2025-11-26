# Pagination - Quick Start Guide

## 🚀 Accessing Paginated Views

### 1. Browse WBS Elements
```
http://localhost:8000/browse/wbs/
```

**Features**:
- 📄 50 WBS elements per page
- 🔍 Search by code or name
- 📊 Statistics panel
- ⚙️ Customizable page size (25/50/100)

**Try**:
- Search: `?search=Project`
- Page 2: `?page=2`
- 100 per page: `?page_size=100`

---

### 2. Browse All Master Data
```
http://localhost:8000/browse/master-data/
```

**Features**:
- 📂 Switch between WBS, Company Codes, Project Types
- 🔍 Unified search across all types
- 📊 Statistics dashboard
- 🔄 Type-specific pagination

**Try**:
- Company Codes: `?type=company_codes`
- Project Types: `?type=project_types`
- Search Companies: `?type=company_codes&search=NL`

---

### 3. Django Admin (Enhanced)
```
http://localhost:8000/admin/reports/wbselement/
```

**Features**:
- 📋 50 items per page
- 🔢 Total count display
- 🔍 Search and filters
- 📑 "Show all" up to 500 items

---

## 💻 Using Pagination in Code

### Simple Pagination

```python
from reports.models import WBSElement
from reports.utils.pagination import paginate_queryset

# Get all WBS elements
queryset = WBSElement.objects.all()

# Paginate (page 1, 25 items)
result = paginate_queryset(queryset, page_number=1, page_size=25)

# Access results
items = result['page_obj']
total = result['total_count']

print(f"Showing {len(items)} of {total} items")
```

### With Search

```python
# Search and paginate
search_term = "Project Alpha"
queryset = WBSElement.objects.filter(name__icontains=search_term)
result = paginate_queryset(queryset, page_number=2, page_size=50)

for item in result['page_obj']:
    print(f"{item.wbs_element}: {item.name}")
```

### Batch Processing

```python
from reports.utils.pagination import chunk_queryset

# Process large dataset in chunks
for chunk in chunk_queryset(WBSElement.objects.all(), chunk_size=1000):
    # Process 1000 items at a time
    for wbs in chunk:
        update_wbs(wbs)
```

---

## 🎨 Using Pagination in Templates

### Include Pagination Component

```django
{% extends 'base.html' %}

{% block content %}
    <!-- Your data table -->
    <table class="table">
        {% for item in page_obj %}
            <tr><td>{{ item.name }}</td></tr>
        {% endfor %}
    </table>

    <!-- Add pagination -->
    {% include 'reports/pagination.html' with page_obj=page_obj paginator=paginator %}
{% endblock %}
```

### In View

```python
from reports.utils.pagination import paginate_queryset

def my_view(request):
    queryset = MyModel.objects.all()
    result = paginate_queryset(
        queryset,
        page_number=request.GET.get('page', 1),
        page_size=request.GET.get('page_size', 50)
    )

    context = {
        **result,  # page_obj, paginator, is_paginated, etc.
    }
    return render(request, 'my_template.html', context)
```

---

## 🧪 Testing

### Run Pagination Tests

```bash
# Run all pagination tests
python manage.py test reports.tests.test_pagination

# Expected output:
# Ran 25 tests in 0.040s
# OK ✅
```

### Run All Tests

```bash
# Run complete test suite
python manage.py test reports.tests

# Expected output:
# Ran 139 tests in 0.236s
# OK ✅
```

---

## ⚙️ Configuration

### settings.py

```python
# Pagination Settings
DEFAULT_PAGE_SIZE = 25   # Default items per page
MAX_PAGE_SIZE = 100      # Maximum allowed
```

### .env (Optional)

```env
DEFAULT_PAGE_SIZE=25
MAX_PAGE_SIZE=100
```

---

## 📊 Available Page Sizes

- **25** - Quick browsing
- **50** - Default for WBS (balanced)
- **100** - Maximum allowed

Users can select from dropdown in UI.

---

## 🎯 Key Features

✅ **Smart Page Ranges**: Shows 5 pages at a time
✅ **First/Last Navigation**: Jump to start/end
✅ **Item Count Display**: "Showing 1 to 50 of 234 entries"
✅ **Query Preservation**: Search terms maintained across pages
✅ **Responsive Design**: Works on mobile and desktop
✅ **Empty State Handling**: Clear messages when no data
✅ **Performance Optimized**: Only loads requested page

---

## 🔧 Quick Tips

1. **Large Datasets**: Use `chunk_queryset()` for batch processing
2. **Custom Sizes**: Enforce `MAX_PAGE_SIZE` to prevent abuse
3. **Search Integration**: Combine with Django's Q objects
4. **URL Bookmarks**: All pagination state in URL parameters
5. **Admin Optimization**: Use `list_select_related` for ForeignKeys

---

## 📚 Full Documentation

See `PAGINATION_IMPLEMENTATION.md` for complete details.

---

**Status**: ✅ Production Ready
**Tests**: 25/25 Passing
**Total Tests**: 139/139 Passing
