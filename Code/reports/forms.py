from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
import os

def validate_file_extension(value):
    """Validate that uploaded file has an allowed extension."""
    ext = os.path.splitext(value.name)[1].lower()
    allowed_extensions = getattr(settings, 'ALLOWED_UPLOAD_EXTENSIONS', ['.dat', '.html', '.xlsx', '.xls'])

    if ext not in allowed_extensions:
        raise ValidationError(
            f'Unsupported file extension "{ext}". Allowed extensions: {", ".join(allowed_extensions)}'
        )

def validate_file_size(value):
    """Validate that uploaded file doesn't exceed maximum size."""
    max_size = getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 104857600)  # 100MB default

    if value.size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        actual_size_mb = value.size / (1024 * 1024)
        raise ValidationError(
            f'File size ({actual_size_mb:.2f} MB) exceeds maximum allowed size ({max_size_mb:.2f} MB)'
        )

class FileUploadForm(forms.Form):
    """A simple form for uploading DAT or HTML files."""
    file = forms.FileField(
        validators=[validate_file_extension, validate_file_size]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        allowed_extensions = getattr(settings, 'ALLOWED_EXTENSIONS', {'.dat': 'DAT files', '.html': 'HTML files'})
        accept = ','.join(allowed_extensions.keys())

        self.fields['file'].widget = forms.FileInput(attrs={'class': 'form-control', 'accept': accept})
        self.fields['file'].label = f"Select a file ({', '.join(allowed_extensions.values())})"

    def clean_file(self):
        """Additional file validation and sanitization."""
        file = self.cleaned_data.get('file')

        if file:
            # Sanitize filename - remove dangerous characters
            original_name = file.name
            safe_name = os.path.basename(original_name)
            # Remove any path traversal attempts
            safe_name = safe_name.replace('..', '').replace('/', '').replace('\\', '')
            file.name = safe_name

        return file


class ExcelUploadForm(forms.Form):
    """Form for uploading Excel files (.xlsx, .xls)."""
    file = forms.FileField(
        validators=[validate_file_extension, validate_file_size]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        allowed_extensions = {'.xlsx': 'Excel files', '.xls': 'Excel files'}
        accept = ','.join(allowed_extensions.keys())

        self.fields['file'].widget = forms.FileInput(attrs={'class': 'form-control', 'accept': accept})
        self.fields['file'].label = f"Select an Excel file ({', '.join(set(allowed_extensions.values()))})"

    def clean_file(self):
        """Additional file validation and sanitization."""
        file = self.cleaned_data.get('file')

        if file:
            # Sanitize filename - remove dangerous characters
            original_name = file.name
            safe_name = os.path.basename(original_name)
            # Remove any path traversal attempts
            safe_name = safe_name.replace('..', '').replace('/', '').replace('\\', '')
            file.name = safe_name

        return file


class ProjectAnalysisUploadForm(forms.Form):
    """Form for uploading two DAT files for Project Analysis report."""
    budget_file = forms.FileField(
        validators=[validate_file_extension, validate_file_size],
        label="Budget File (All_Projects.DAT)"
    )
    plan_file = forms.FileField(
        validators=[validate_file_extension, validate_file_size],
        label="Plan/Actual File (All_Projects_Plan.DAT)"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only accept DAT files for this report
        accept = '.dat'

        self.fields['budget_file'].widget = forms.FileInput(
            attrs={'class': 'form-control', 'accept': accept}
        )
        self.fields['plan_file'].widget = forms.FileInput(
            attrs={'class': 'form-control', 'accept': accept}
        )

    def clean_budget_file(self):
        """Sanitize budget file name."""
        file = self.cleaned_data.get('budget_file')
        if file:
            safe_name = os.path.basename(file.name)
            safe_name = safe_name.replace('..', '').replace('/', '').replace('\\', '')
            file.name = safe_name
        return file

    def clean_plan_file(self):
        """Sanitize plan file name."""
        file = self.cleaned_data.get('plan_file')
        if file:
            safe_name = os.path.basename(file.name)
            safe_name = safe_name.replace('..', '').replace('/', '').replace('\\', '')
            file.name = safe_name
        return file
