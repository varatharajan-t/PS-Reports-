from django import forms
from django.conf import settings

class FileUploadForm(forms.Form):
    """A simple form for uploading DAT or HTML files."""
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        allowed_extensions = getattr(settings, 'ALLOWED_EXTENSIONS', {'.dat': 'DAT files', '.html': 'HTML files'})
        accept = ','.join(allowed_extensions.keys())

        self.fields['file'].widget = forms.FileInput(attrs={'class': 'form-control', 'accept': accept})
        self.fields['file'].label = f"Select a file ({', '.join(allowed_extensions.values())})"


class ExcelUploadForm(forms.Form):
    """Form for uploading Excel files (.xlsx, .xls)."""
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        allowed_extensions = {'.xlsx': 'Excel files', '.xls': 'Excel files'}
        accept = ','.join(allowed_extensions.keys())

        self.fields['file'].widget = forms.FileInput(attrs={'class': 'form-control', 'accept': accept})
        self.fields['file'].label = f"Select an Excel file ({', '.join(set(allowed_extensions.values()))})"
