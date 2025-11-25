from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.http import FileResponse, Http404
import os
from .forms import FileUploadForm, ExcelUploadForm
from .services.budget_report_service import generate_budget_report
from .services.budget_updates_service import generate_budget_updates_report
from .services.budget_variance_service import generate_budget_variance_report
from .services.project_type_wise_service import generate_project_type_wise_report
from .services.glimps_of_projects_service import generate_glimps_of_projects_report
from .services.plan_variance_service import generate_plan_variance_report

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
    NOTE: Backend processing for this report is not yet implemented.
    """
    context = {
        'form': FileUploadForm(),
        'page_title': 'Generate Project Analysis Report',
        'processed_file': None
    }
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            context['processed_file'] = uploaded_file.name
            context['not_implemented'] = True
            context['form'] = FileUploadForm() 
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
                report_data = generate_glimps_of_projects_report(uploaded_file_path)
                context['report_file_name'] = os.path.basename(report_data["file_path"])
                context['data_html'] = report_data["data_html"]
            except Exception as e:
                context['error'] = str(e)
            finally:
                fs.delete(filename)
            context['form'] = FileUploadForm()
    return render(request, 'reports/report_glimps_of_projects.html', context)
