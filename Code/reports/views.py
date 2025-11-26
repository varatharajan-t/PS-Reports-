from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.http import FileResponse, Http404
import os
from .forms import FileUploadForm, ExcelUploadForm, ProjectAnalysisUploadForm
from .models import WBSElement, CompanyCode, ProjectType
from .utils.pagination import paginate_queryset
from .services.budget_report_service import generate_budget_report
from .services.budget_updates_service import generate_budget_updates_report
from .services.budget_variance_service import generate_budget_variance_report
from .services.project_type_wise_service import generate_project_type_wise_report
from .services.glimps_of_projects_service import generate_glimps_of_projects_report
from .services.plan_variance_service import generate_plan_variance_report
from .services.project_analysis_service import generate_project_analysis_report

def dashboard(request):
    """
    Renders the main dashboard page, which displays a list of available reports.
    This view replaces the main menu from the original desktop application.
    """
    report_list = [
        {'name': 'Budget Report', 'url_name': 'report_budget'},
        {'name': 'Budget Updates', 'url_name': 'report_budget_updates'},
        {'name': 'Budget Variance', 'url_name': 'report_budget_variance'},
        {'name': 'Project Type Wise', 'url_name': 'report_project_type_wise'},
        {'name': 'Glimps of Projects', 'url_name': 'report_glimps_of_projects'},
        {'name': 'Plan Variance', 'url_name': 'report_plan_variance'},
        {'name': 'Project Analysis', 'url_name': 'report_project_analysis'},
    ]
    context = {
        'reports': report_list,
        'page_title': 'SAP Project System Reports Dashboard'
    }
    return render(request, 'reports/dashboard.html', context)

def budget_report_view(request):
    """
    Handles the file upload and processing for the Budget Report.
    """
    context = {
        'form': FileUploadForm(),
        'page_title': 'Generate Budget Report',
        'report_file_name': None,
        'data_html': None
    }
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            fs = FileSystemStorage(location=settings.BASE_DIR / 'data' / 'uploads')
            filename = fs.save(uploaded_file.name, uploaded_file)
            uploaded_file_path = fs.path(filename)
            try:
                report_data = generate_budget_report(uploaded_file_path)
                context['report_file_name'] = os.path.basename(report_data["file_path"])
                context['data_html'] = report_data["data_html"]
            except Exception as e:
                context['error'] = str(e)
            finally:
                fs.delete(filename)
            context['form'] = FileUploadForm() 
    return render(request, 'reports/report_budget.html', context)

def download_report_view(request, filename):
    """
    Serves a generated report file for download.
    """
    file_path = settings.BASE_DIR / 'data' / 'reports' / filename
    if not os.path.exists(file_path):
        raise Http404("File not found.")

    # FileResponse will automatically close the file after sending
    response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
    return response

def plan_variance_report_view(request):
    """
    Handles the file upload and processing for the Plan Variance Report.
    Processes DAT files and creates formatted Excel reports.
    """
    context = {
        'form': FileUploadForm(),
        'page_title': 'Generate Plan Variance Report',
        'report_file_name': None,
        'data_html': None
    }
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            fs = FileSystemStorage(location=settings.BASE_DIR / 'data' / 'uploads')
            filename = fs.save(uploaded_file.name, uploaded_file)
            uploaded_file_path = fs.path(filename)
            try:
                report_data = generate_plan_variance_report(uploaded_file_path)
                context['report_file_name'] = os.path.basename(report_data["file_path"])
                context['data_html'] = report_data["data_html"]
            except Exception as e:
                context['error'] = str(e)
            finally:
                fs.delete(filename)
            context['form'] = FileUploadForm()
    return render(request, 'reports/report_plan_variance.html', context)

def project_analysis_report_view(request):
    """
    Handles the file upload for the Project Analysis Report.
    Requires TWO DAT files: Budget and Plan/Actual.
    """
    context = {
        'form': ProjectAnalysisUploadForm(),
        'page_title': 'Generate Project Analysis Report',
        'report_file_name': None,
        'data_html': None
    }
    if request.method == 'POST':
        form = ProjectAnalysisUploadForm(request.POST, request.FILES)
        if form.is_valid():
            budget_file = request.FILES['budget_file']
            plan_file = request.FILES['plan_file']

            fs = FileSystemStorage(location=settings.BASE_DIR / 'data' / 'uploads')

            # Save both files
            budget_filename = fs.save(budget_file.name, budget_file)
            plan_filename = fs.save(plan_file.name, plan_file)

            budget_file_path = fs.path(budget_filename)
            plan_file_path = fs.path(plan_filename)

            try:
                report_data = generate_project_analysis_report(budget_file_path, plan_file_path)
                context['report_file_name'] = os.path.basename(report_data["file_path"])
                context['data_html'] = report_data["data_html"]
                context['stats'] = {
                    'rows_processed': report_data.get('rows_processed', 0),
                    'budget_projects': report_data.get('budget_projects', 0),
                    'actual_projects': report_data.get('actual_projects', 0),
                }
            except Exception as e:
                context['error'] = str(e)
            finally:
                # Clean up uploaded files
                fs.delete(budget_filename)
                fs.delete(plan_filename)

            context['form'] = ProjectAnalysisUploadForm()
    return render(request, 'reports/report_project_analysis.html', context)

def budget_updates_report_view(request):
    """
    Handles the file upload and processing for the Budget Updates Report.
    """
    context = {
        'form': FileUploadForm(),
        'page_title': 'Generate Budget Updates Report',
        'report_file_name': None,
        'data_html': None
    }
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            fs = FileSystemStorage(location=settings.BASE_DIR / 'data' / 'uploads')
            filename = fs.save(uploaded_file.name, uploaded_file)
            uploaded_file_path = fs.path(filename)
            try:
                report_data = generate_budget_updates_report(uploaded_file_path)
                context['report_file_name'] = os.path.basename(report_data["file_path"])
                context['data_html'] = report_data["data_html"]
            except Exception as e:
                context['error'] = str(e)
            finally:
                fs.delete(filename)
            context['form'] = FileUploadForm()
    return render(request, 'reports/report_budget_updates.html', context)

def budget_variance_report_view(request):
    """
    Handles the file upload and processing for the Budget Variance Report.
    Processes HTML files (not DAT files).
    """
    context = {
        'form': FileUploadForm(),
        'page_title': 'Generate Budget Variance Report',
        'report_file_name': None,
        'data_html': None
    }
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            fs = FileSystemStorage(location=settings.BASE_DIR / 'data' / 'uploads')
            filename = fs.save(uploaded_file.name, uploaded_file)
            uploaded_file_path = fs.path(filename)
            try:
                report_data = generate_budget_variance_report(uploaded_file_path)
                context['report_file_name'] = os.path.basename(report_data["file_path"])
                context['data_html'] = report_data["data_html"]
            except Exception as e:
                context['error'] = str(e)
            finally:
                fs.delete(filename)
            context['form'] = FileUploadForm()
    return render(request, 'reports/report_budget_variance.html', context)

def project_type_wise_report_view(request):
    """
    Handles the file upload and processing for the Project Type Wise Report.
    Processes Excel files and creates hyperlinked multi-sheet reports.
    """
    context = {
        'form': ExcelUploadForm(),
        'page_title': 'Generate Project Type Wise Report',
        'report_file_name': None,
        'data_html': None
    }
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            fs = FileSystemStorage(location=settings.BASE_DIR / 'data' / 'uploads')
            filename = fs.save(uploaded_file.name, uploaded_file)
            uploaded_file_path = fs.path(filename)
            try:
                report_data = generate_project_type_wise_report(uploaded_file_path)
                context['report_file_name'] = os.path.basename(report_data["file_path"])
                context['data_html'] = report_data["data_html"]
            except Exception as e:
                context['error'] = str(e)
            finally:
                fs.delete(filename)
            context['form'] = ExcelUploadForm()
    return render(request, 'reports/report_project_type_wise.html', context)

def glimps_of_projects_report_view(request):
    """
    Handles the file upload and processing for the Glimps of Projects Report.
    Creates interactive analytics dashboard with cross-tabulation and charts.
    """
    context = {
        'form': FileUploadForm(),
        'page_title': 'Generate Glimps of Projects Report',
        'report_file_name': None,
        'data_html': None,
        'chart_script': None
    }
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            fs = FileSystemStorage(location=settings.BASE_DIR / 'data' / 'uploads')
            filename = fs.save(uploaded_file.name, uploaded_file)
            uploaded_file_path = fs.path(filename)
            try:
                report_data = generate_glimps_of_projects_report(uploaded_file_path)
                context['report_file_name'] = os.path.basename(report_data["file_path"])
                context['data_html'] = report_data["data_html"]
                context['chart_script'] = report_data["chart_script"]
            except Exception as e:
                context['error'] = str(e)
            finally:
                fs.delete(filename)
            context['form'] = FileUploadForm()
    return render(request, 'reports/report_glimps_of_projects.html', context)

def browse_wbs_elements(request):
    """
    Browse WBS Elements with pagination support.
    Demonstrates pagination for large datasets.
    """
    # Get query parameters
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 50)
    search_query = request.GET.get('search', '')
    
    # Build queryset
    queryset = WBSElement.objects.all()
    
    # Apply search filter if provided
    if search_query:
        queryset = queryset.filter(
            wbs_element__icontains=search_query
        ) | queryset.filter(
            name__icontains=search_query
        )
    
    # Paginate the queryset
    try:
        page_size = int(page_size)
    except (ValueError, TypeError):
        page_size = 50
    
    pagination_data = paginate_queryset(queryset, page_number, page_size)
    
    context = {
        'page_title': 'Browse WBS Elements',
        'search_query': search_query,
        'page_size': page_size,
        **pagination_data,  # Unpacks page_obj, paginator, is_paginated, etc.
    }
    
    return render(request, 'reports/browse_wbs.html', context)


def browse_master_data(request):
    """
    Browse all master data (Company Codes, Project Types, WBS Elements) with pagination.
    """
    # Determine which data type to show
    data_type = request.GET.get('type', 'wbs')
    page_number = request.GET.get('page', 1)
    search_query = request.GET.get('search', '')
    
    # Get the appropriate queryset
    if data_type == 'company_codes':
        queryset = CompanyCode.objects.all()
        if search_query:
            queryset = queryset.filter(code__icontains=search_query) | queryset.filter(name__icontains=search_query)
        page_size = 25
    elif data_type == 'project_types':
        queryset = ProjectType.objects.all()
        if search_query:
            queryset = queryset.filter(code__icontains=search_query) | queryset.filter(name__icontains=search_query)
        page_size = 25
    else:  # default to WBS elements
        queryset = WBSElement.objects.all()
        if search_query:
            queryset = queryset.filter(wbs_element__icontains=search_query) | queryset.filter(name__icontains=search_query)
        page_size = 50
    
    # Paginate
    pagination_data = paginate_queryset(queryset, page_number, page_size)
    
    context = {
        'page_title': 'Browse Master Data',
        'data_type': data_type,
        'search_query': search_query,
        **pagination_data,
    }
    
    return render(request, 'reports/browse_master_data.html', context)
