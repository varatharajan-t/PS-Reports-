# Django Migration Plan - SAP Reporting System

## Project Overview

Convert the existing Python desktop application into a Django-based web application with the following goals:
- Web interface for file uploads and report generation
- User authentication and report history
- Asynchronous processing for large files
- Interactive dashboards
- API endpoints for integration

## Phase 1: Project Setup & Architecture Design

### 1.1 Create Django Project Structure

```bash
# Install Django and dependencies
pip install django==5.0
pip install celery redis  # For async task processing
pip install django-crispy-forms crispy-bootstrap5  # For better forms
pip install django-tables2  # For data tables
pip install plotly  # For interactive charts
pip install django-storages boto3  # Optional: for cloud storage

# Create Django project
django-admin startproject sap_reports
cd sap_reports

# Create apps for different modules
python manage.py startapp core          # Core functionality
python manage.py startapp reports       # Report processing
python manage.py startapp dashboard     # Analytics dashboard
python manage.py startapp accounts      # User management
```

### 1.2 Recommended Project Structure

```
sap_reports/
├── manage.py
├── sap_reports/              # Project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core/                     # Core app
│   ├── processors/           # Data processing logic
│   │   ├── __init__.py
│   │   ├── base.py          # From data_processor_base.py
│   │   ├── wbs.py           # WBS processing
│   │   └── excel.py         # Excel formatting
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py        # From config.py
│   │   └── validators.py    # File validation
│   └── management/
│       └── commands/         # CLI commands
├── reports/                  # Reports app
│   ├── models.py            # Report models
│   ├── views.py             # Report views
│   ├── forms.py             # Upload forms
│   ├── tasks.py             # Celery tasks
│   ├── services/            # Business logic
│   │   ├── budget_report.py
│   │   ├── budget_updates.py
│   │   ├── budget_variance.py
│   │   ├── plan_variance.py
│   │   ├── project_analysis.py
│   │   ├── project_typewise.py
│   │   └── year_end.py
│   └── templates/reports/
│       ├── upload.html
│       ├── list.html
│       ├── detail.html
│       └── download.html
├── dashboard/               # Dashboard app
│   ├── views.py
│   ├── services/
│   │   └── glimps_analytics.py
│   └── templates/dashboard/
│       ├── home.html
│       └── analytics.html
├── accounts/                # User management
│   ├── models.py
│   ├── views.py
│   └── templates/accounts/
├── static/
│   ├── css/
│   ├── js/
│   └── img/
├── media/                   # User uploaded files
│   ├── uploads/
│   ├── master_data/        # WBS_NAMES.XLSX
│   └── reports/            # Generated reports
├── templates/              # Global templates
│   └── base.html
└── requirements.txt
```

## Phase 2: Database Models

### 2.1 Define Django Models

Create models in `reports/models.py`:

```python
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator

class MasterData(models.Model):
    """Master WBS data (replaces WBS_NAMES.XLSX)"""
    wbs_element = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=500)
    company_code = models.CharField(max_length=10, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'master_wbs_data'
        indexes = [models.Index(fields=['wbs_element'])]

class Report(models.Model):
    """Track all generated reports"""
    REPORT_TYPES = [
        ('budget_report', 'Budget Report'),
        ('budget_updates', 'Budget Updates'),
        ('budget_variance', 'Budget Variance'),
        ('plan_variance', 'Plan Variance'),
        ('glimps', 'Glimps of Projects'),
        ('project_analysis', 'Project Analysis'),
        ('project_typewise', 'Project Type Wise'),
        ('year_end', 'Year End 558'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    input_file = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['dat', 'html', 'xlsx'])]
    )
    output_file = models.FileField(upload_to='reports/%Y/%m/%d/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    error_message = models.TextField(blank=True)
    processing_log = models.TextField(blank=True)

    # Metadata
    record_count = models.IntegerField(null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'reports'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_type', 'status']),
            models.Index(fields=['created_by', '-created_at']),
        ]

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.created_at}"

class WBSElement(models.Model):
    """Store processed WBS elements from reports"""
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='wbs_elements')
    wbs_id = models.CharField(max_length=100, db_index=True)
    description = models.CharField(max_length=500)
    is_summary = models.BooleanField(default=False)
    level = models.IntegerField(default=0)
    parent_wbs = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'wbs_elements'
        indexes = [
            models.Index(fields=['report', 'wbs_id']),
            models.Index(fields=['is_summary']),
        ]

class ProjectData(models.Model):
    """Store project information for analytics"""
    project_id = models.CharField(max_length=100, unique=True, db_index=True)
    company_code = models.CharField(max_length=10)
    company_name = models.CharField(max_length=100)
    project_type_code = models.CharField(max_length=10)
    project_type_name = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_data'
        indexes = [
            models.Index(fields=['company_code', 'project_type_code']),
        ]
```

### 2.2 Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## Phase 3: Core Business Logic Migration

### 3.1 Convert Existing Code to Services

Move existing processing logic to service classes in `reports/services/`:

**Example: `reports/services/budget_report.py`**

```python
from core.processors.base import BaseDataProcessor
from core.processors.wbs import WBSProcessor
from core.processors.excel import ExcelFormatter
from reports.models import Report, WBSElement
from django.core.files.base import ContentFile
import tempfile
import os

class BudgetReportService:
    """Service for Budget Report processing"""

    def __init__(self, report_instance):
        self.report = report_instance
        self.processor = BaseDataProcessor('BudgetReport')
        self.wbs_processor = WBSProcessor()

    def process(self):
        """Main processing method"""
        try:
            # Update status
            self.report.status = 'processing'
            self.report.save()

            # Create temp files
            with tempfile.TemporaryDirectory() as temp_dir:
                input_path = self._save_temp_file(self.report.input_file, temp_dir)
                cleaned_path = os.path.join(temp_dir, 'cleaned.dat')
                output_path = os.path.join(temp_dir, 'output.xlsx')

                # Process data (use existing logic)
                self._clean_data(input_path, cleaned_path)
                df = self._read_data(cleaned_path)
                df = self._transform_data(df)

                # Generate Excel
                self._generate_excel(df, output_path)

                # Save output to model
                with open(output_path, 'rb') as f:
                    self.report.output_file.save(
                        f"{self.report.report_type}_{self.report.id}.xlsx",
                        ContentFile(f.read())
                    )

                # Update status
                self.report.status = 'completed'
                self.report.record_count = len(df)
                self.report.save()

                # Store WBS elements
                self._save_wbs_elements(df)

            return True

        except Exception as e:
            self.report.status = 'failed'
            self.report.error_message = str(e)
            self.report.save()
            raise

    def _clean_data(self, input_path, output_path):
        """Clean DAT file - reuse existing logic from BudgetReport.py"""
        # Copy logic from existing clean_data method
        pass

    def _read_data(self, file_path):
        """Read data - reuse existing logic"""
        # Copy logic from existing read_data method
        pass

    def _transform_data(self, df):
        """Transform data - reuse existing logic"""
        # Copy logic from existing transform_data method
        pass

    def _generate_excel(self, df, output_path):
        """Generate Excel file - reuse existing logic"""
        # Copy logic from ExcelFormatter
        pass

    def _save_wbs_elements(self, df):
        """Save WBS elements to database"""
        wbs_list = df['WBS_element'].unique().tolist()
        summary_wbs, transaction_wbs = self.wbs_processor.classify_wbs_elements(wbs_list)

        for wbs in wbs_list:
            WBSElement.objects.create(
                report=self.report,
                wbs_id=wbs,
                is_summary=wbs in summary_wbs
            )

    def _save_temp_file(self, uploaded_file, temp_dir):
        """Save uploaded file to temp location"""
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        return temp_path
```

### 3.2 Service Factory Pattern

Create `reports/services/factory.py`:

```python
from .budget_report import BudgetReportService
from .budget_updates import BudgetUpdatesService
from .budget_variance import BudgetVarianceService
# ... import other services

class ReportServiceFactory:
    """Factory to get appropriate service for report type"""

    SERVICES = {
        'budget_report': BudgetReportService,
        'budget_updates': BudgetUpdatesService,
        'budget_variance': BudgetVarianceService,
        'plan_variance': PlanVarianceService,
        'glimps': GlimpsAnalyticsService,
        'project_analysis': ProjectAnalysisService,
        'project_typewise': ProjectTypeWiseService,
        'year_end': YearEndService,
    }

    @classmethod
    def get_service(cls, report_instance):
        """Get service instance for report type"""
        service_class = cls.SERVICES.get(report_instance.report_type)
        if not service_class:
            raise ValueError(f"Unknown report type: {report_instance.report_type}")
        return service_class(report_instance)
```

## Phase 4: Asynchronous Task Processing

### 4.1 Setup Celery

**Install and configure:**

```bash
# Install
pip install celery redis django-celery-results

# Add to settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
```

**Create `sap_reports/celery.py`:**

```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sap_reports.settings')
app = Celery('sap_reports')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

### 4.2 Create Celery Tasks

**In `reports/tasks.py`:**

```python
from celery import shared_task
from .models import Report
from .services.factory import ReportServiceFactory
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_report_task(self, report_id):
    """Asynchronous task to process reports"""
    try:
        report = Report.objects.get(id=report_id)
        service = ReportServiceFactory.get_service(report)
        service.process()

        logger.info(f"Report {report_id} processed successfully")
        return {'status': 'success', 'report_id': report_id}

    except Report.DoesNotExist:
        logger.error(f"Report {report_id} not found")
        return {'status': 'error', 'message': 'Report not found'}

    except Exception as e:
        logger.error(f"Error processing report {report_id}: {str(e)}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
```

### 4.3 Run Celery Worker

```bash
# In separate terminal
celery -A sap_reports worker -l info
```

## Phase 5: Web Interface (Views & Templates)

### 5.1 Create Forms

**In `reports/forms.py`:**

```python
from django import forms
from .models import Report

class ReportUploadForm(forms.ModelForm):
    """Form for uploading report files"""

    class Meta:
        model = Report
        fields = ['report_type', 'input_file']
        widgets = {
            'report_type': forms.Select(attrs={'class': 'form-select'}),
            'input_file': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_input_file(self):
        file = self.cleaned_data['input_file']
        report_type = self.cleaned_data.get('report_type')

        # Validate file extension based on report type
        if report_type == 'budget_variance' and not file.name.endswith('.html'):
            raise forms.ValidationError('Budget Variance requires HTML file')
        elif report_type != 'budget_variance' and not file.name.endswith('.dat'):
            raise forms.ValidationError('This report type requires DAT file')

        # Validate file size (e.g., max 50MB)
        if file.size > 50 * 1024 * 1024:
            raise forms.ValidationError('File size must be under 50MB')

        return file

class MasterDataUploadForm(forms.Form):
    """Form for uploading WBS master data"""
    file = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['xlsx'])],
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
```

### 5.2 Create Views

**In `reports/views.py`:**

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, JsonResponse
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Report
from .forms import ReportUploadForm
from .tasks import process_report_task

@login_required
def upload_report(request):
    """Upload and process report file"""
    if request.method == 'POST':
        form = ReportUploadForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.created_by = request.user
            report.file_size = report.input_file.size
            report.save()

            # Trigger async processing
            process_report_task.delay(report.id)

            messages.success(request, 'Report uploaded successfully. Processing has started.')
            return redirect('reports:detail', pk=report.id)
    else:
        form = ReportUploadForm()

    return render(request, 'reports/upload.html', {'form': form})

class ReportListView(LoginRequiredMixin, ListView):
    """List all reports for current user"""
    model = Report
    template_name = 'reports/list.html'
    context_object_name = 'reports'
    paginate_by = 20

    def get_queryset(self):
        return Report.objects.filter(created_by=self.request.user)

class ReportDetailView(LoginRequiredMixin, DetailView):
    """View report details and download"""
    model = Report
    template_name = 'reports/detail.html'
    context_object_name = 'report'

    def get_queryset(self):
        return Report.objects.filter(created_by=self.request.user)

@login_required
def download_report(request, pk):
    """Download generated report file"""
    report = get_object_or_404(Report, pk=pk, created_by=request.user)

    if report.status != 'completed' or not report.output_file:
        messages.error(request, 'Report is not ready for download')
        return redirect('reports:detail', pk=pk)

    return FileResponse(
        report.output_file.open('rb'),
        as_attachment=True,
        filename=f"{report.get_report_type_display()}_{report.id}.xlsx"
    )

@login_required
def report_status(request, pk):
    """AJAX endpoint to check report processing status"""
    report = get_object_or_404(Report, pk=pk, created_by=request.user)
    return JsonResponse({
        'status': report.status,
        'error_message': report.error_message,
        'download_url': report.output_file.url if report.output_file else None
    })
```

### 5.3 Create Templates

**Base template: `templates/base.html`:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}SAP Reporting System{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{% url 'dashboard:home' %}">SAP Reports</a>
            <div class="navbar-nav ms-auto">
                {% if user.is_authenticated %}
                    <a class="nav-link" href="{% url 'reports:list' %}">My Reports</a>
                    <a class="nav-link" href="{% url 'reports:upload' %}">Upload</a>
                    <a class="nav-link" href="{% url 'dashboard:analytics' %}">Dashboard</a>
                    <a class="nav-link" href="{% url 'accounts:logout' %}">Logout ({{ user.username }})</a>
                {% else %}
                    <a class="nav-link" href="{% url 'accounts:login' %}">Login</a>
                {% endif %}
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}

        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

**Upload template: `reports/templates/reports/upload.html`:**

```html
{% extends 'base.html' %}

{% block title %}Upload Report{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h3>Upload Report File</h3>
            </div>
            <div class="card-body">
                <form method="post" enctype="multipart/form-data">
                    {% csrf_token %}

                    <div class="mb-3">
                        <label for="{{ form.report_type.id_for_label }}" class="form-label">Report Type</label>
                        {{ form.report_type }}
                        {% if form.report_type.errors %}
                            <div class="text-danger">{{ form.report_type.errors }}</div>
                        {% endif %}
                    </div>

                    <div class="mb-3">
                        <label for="{{ form.input_file.id_for_label }}" class="form-label">Input File</label>
                        {{ form.input_file }}
                        <div class="form-text">
                            Upload .dat file (or .html for Budget Variance). Max size: 50MB
                        </div>
                        {% if form.input_file.errors %}
                            <div class="text-danger">{{ form.input_file.errors }}</div>
                        {% endif %}
                    </div>

                    <button type="submit" class="btn btn-primary">Upload & Process</button>
                    <a href="{% url 'reports:list' %}" class="btn btn-secondary">Cancel</a>
                </form>
            </div>
        </div>

        <div class="card mt-4">
            <div class="card-header">
                <h5>Report Types</h5>
            </div>
            <div class="card-body">
                <ul>
                    <li><strong>Budget Report:</strong> Standard SAP budget processing</li>
                    <li><strong>Budget Updates:</strong> Budget modification tracking</li>
                    <li><strong>Budget Variance:</strong> Budget vs actual variance (HTML input)</li>
                    <li><strong>Plan Variance:</strong> Plan vs execution variance</li>
                    <li><strong>Glimps of Projects:</strong> Interactive analytics dashboard</li>
                    <li><strong>Project Analysis:</strong> Comprehensive project analysis</li>
                    <li><strong>Project Type Wise:</strong> Project classification</li>
                    <li><strong>Year End 558:</strong> Year-end financial extraction</li>
                </ul>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

**Detail template with auto-refresh: `reports/templates/reports/detail.html`:**

```html
{% extends 'base.html' %}

{% block title %}Report Details{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h3>Report Details</h3>
                <span class="badge bg-{{ report.status|status_badge }}" id="status-badge">
                    {{ report.get_status_display }}
                </span>
            </div>
            <div class="card-body">
                <table class="table">
                    <tr>
                        <th>Report Type:</th>
                        <td>{{ report.get_report_type_display }}</td>
                    </tr>
                    <tr>
                        <th>Input File:</th>
                        <td>{{ report.input_file.name }}</td>
                    </tr>
                    <tr>
                        <th>File Size:</th>
                        <td>{{ report.file_size|filesizeformat }}</td>
                    </tr>
                    <tr>
                        <th>Created:</th>
                        <td>{{ report.created_at }}</td>
                    </tr>
                    <tr>
                        <th>Status:</th>
                        <td id="status-text">{{ report.get_status_display }}</td>
                    </tr>
                    {% if report.processed_at %}
                    <tr>
                        <th>Processed:</th>
                        <td>{{ report.processed_at }}</td>
                    </tr>
                    {% endif %}
                    {% if report.record_count %}
                    <tr>
                        <th>Records Processed:</th>
                        <td>{{ report.record_count }}</td>
                    </tr>
                    {% endif %}
                </table>

                {% if report.status == 'completed' %}
                    <a href="{% url 'reports:download' report.id %}" class="btn btn-success">
                        Download Excel Report
                    </a>
                {% elif report.status == 'failed' %}
                    <div class="alert alert-danger">
                        <strong>Error:</strong> {{ report.error_message }}
                    </div>
                {% elif report.status == 'processing' %}
                    <div class="alert alert-info">
                        <div class="spinner-border spinner-border-sm me-2"></div>
                        Processing... This page will auto-update.
                    </div>
                {% endif %}

                <a href="{% url 'reports:list' %}" class="btn btn-secondary">Back to List</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
{% if report.status == 'processing' or report.status == 'pending' %}
<script>
// Auto-refresh status every 3 seconds
setInterval(function() {
    fetch("{% url 'reports:status' report.id %}")
        .then(response => response.json())
        .then(data => {
            document.getElementById('status-text').textContent = data.status;

            if (data.status === 'completed') {
                location.reload();
            } else if (data.status === 'failed') {
                location.reload();
            }
        });
}, 3000);
</script>
{% endif %}
{% endblock %}
```

## Phase 6: Dashboard & Analytics

### 6.1 Dashboard View

**In `dashboard/views.py`:**

```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from reports.models import Report, ProjectData
import plotly.graph_objects as go
import plotly.express as px

@login_required
def home(request):
    """Dashboard home with statistics"""
    user_reports = Report.objects.filter(created_by=request.user)

    stats = {
        'total_reports': user_reports.count(),
        'completed': user_reports.filter(status='completed').count(),
        'processing': user_reports.filter(status='processing').count(),
        'failed': user_reports.filter(status='failed').count(),
    }

    # Report type distribution
    report_dist = user_reports.values('report_type').annotate(count=Count('id'))

    return render(request, 'dashboard/home.html', {
        'stats': stats,
        'report_distribution': report_dist
    })

@login_required
def analytics(request):
    """Interactive analytics dashboard (replaces GlimpsOfProjects)"""
    # Get project data
    projects = ProjectData.objects.all()

    # Create cross-tabulation
    df = pd.DataFrame(list(projects.values()))
    if not df.empty:
        crosstab = pd.crosstab(
            df['project_type_name'],
            df['company_name'],
            margins=True
        )

        # Create interactive chart using Plotly
        fig = px.bar(
            df,
            x='company_name',
            y='project_type_name',
            color='project_type_name',
            title='Project Distribution'
        )
        chart_html = fig.to_html()
    else:
        chart_html = None

    return render(request, 'dashboard/analytics.html', {
        'chart': chart_html
    })
```

## Phase 7: URLs Configuration

**Main `sap_reports/urls.py`:**

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('reports/', include('reports.urls')),
    path('accounts/', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

**`reports/urls.py`:**

```python
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportListView.as_view(), name='list'),
    path('upload/', views.upload_report, name='upload'),
    path('<int:pk>/', views.ReportDetailView.as_view(), name='detail'),
    path('<int:pk>/download/', views.download_report, name='download'),
    path('<int:pk>/status/', views.report_status, name='status'),
]
```

## Phase 8: Deployment Preparation

### 8.1 Update Settings

**In `sap_reports/settings.py`:**

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'crispy_forms',
    'crispy_bootstrap5',
    'django_celery_results',

    # Local apps
    'core',
    'reports',
    'dashboard',
    'accounts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# File upload settings
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50 MB

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'reports': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

### 8.2 Create Requirements File

**`requirements.txt`:**

```txt
Django==5.0
pandas>=1.3.0
openpyxl>=3.0.0
celery>=5.3.0
redis>=4.5.0
django-celery-results>=2.5.0
django-crispy-forms>=2.0
crispy-bootstrap5>=0.7
plotly>=5.14.0
Pillow>=10.0.0
python-dateutil>=2.8.2
```

## Phase 9: Migration Steps

### Step-by-Step Migration Process

1. **Setup Django Project**
   ```bash
   cd D:\PS-Reports
   mkdir django_app
   cd django_app
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   django-admin startproject sap_reports .
   python manage.py startapp core
   python manage.py startapp reports
   python manage.py startapp dashboard
   python manage.py startapp accounts
   ```

2. **Copy Existing Code**
   - Copy processing logic from `.py` files to service classes
   - Copy `config.py` to `core/utils/config.py`
   - Copy error handling to `core/utils/error_handler.py`
   - Adapt each report module to service class pattern

3. **Setup Database**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Load Master Data**
   - Create management command to import WBS_NAMES.XLSX
   - Or create admin interface for uploading

5. **Setup Celery**
   ```bash
   # Install Redis (Windows: download from GitHub)
   # Start Redis server
   redis-server

   # In new terminal, start Celery worker
   celery -A sap_reports worker -l info
   ```

6. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

7. **Test Each Report Type**
   - Upload sample files
   - Verify processing
   - Test download functionality

## Phase 10: Additional Features

### 10.1 API Endpoints (Optional)

Create REST API using Django REST Framework:

```bash
pip install djangorestframework

# In reports/api/serializers.py
from rest_framework import serializers
from reports.models import Report

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'

# In reports/api/views.py
from rest_framework import viewsets
from reports.models import Report
from .serializers import ReportSerializer

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
```

### 10.2 Scheduled Tasks

Add periodic tasks for cleanup:

```python
# In reports/tasks.py
from celery import shared_task
from datetime import timedelta
from django.utils import timezone

@shared_task
def cleanup_old_reports():
    """Delete reports older than 30 days"""
    threshold = timezone.now() - timedelta(days=30)
    old_reports = Report.objects.filter(created_at__lt=threshold)
    count = old_reports.count()
    old_reports.delete()
    return f"Deleted {count} old reports"
```

### 10.3 Email Notifications

Send email when processing completes:

```python
# In reports/tasks.py
from django.core.mail import send_mail

@shared_task
def send_completion_email(report_id):
    """Send email when report is ready"""
    report = Report.objects.get(id=report_id)
    send_mail(
        subject=f'Report Ready: {report.get_report_type_display()}',
        message=f'Your report has been processed and is ready for download.',
        from_email='noreply@example.com',
        recipient_list=[report.created_by.email],
    )
```

## Summary

This migration plan provides a complete roadmap to convert your desktop application into a modern Django web application. The key advantages:

- **Web Access**: Access from anywhere, no desktop installation needed
- **Multi-User**: User authentication and report history
- **Scalability**: Async processing handles large files efficiently
- **Maintainability**: Clear separation of concerns with Django apps
- **Analytics**: Interactive dashboards with Plotly
- **API Ready**: Easy to add REST API endpoints

Start with Phase 1-3 to get the core working, then progressively add features from later phases.
