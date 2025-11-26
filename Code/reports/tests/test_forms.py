"""
Tests for reports app forms.
"""
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from reports.forms import FileUploadForm, ExcelUploadForm, ProjectAnalysisUploadForm


class FileUploadFormTest(TestCase):
    """Tests for FileUploadForm."""

    def test_valid_dat_file(self):
        """Test form with a valid .dat file."""
        file_content = b"header\ndata"
        uploaded_file = SimpleUploadedFile("test.dat", file_content, content_type="text/plain")
        form = FileUploadForm(files={'file': uploaded_file})
        self.assertTrue(form.is_valid())

    def test_valid_html_file(self):
        """Test form with a valid .html file."""
        file_content = b"<html><body>test</body></html>"
        uploaded_file = SimpleUploadedFile("test.html", file_content, content_type="text/html")
        form = FileUploadForm(files={'file': uploaded_file})
        self.assertTrue(form.is_valid())

    def test_invalid_file_extension(self):
        """Test form with an invalid file extension."""
        file_content = b"test content"
        uploaded_file = SimpleUploadedFile("test.txt", file_content, content_type="text/plain")
        form = FileUploadForm(files={'file': uploaded_file})
        self.assertFalse(form.is_valid())
        self.assertIn('file', form.errors)

    def test_file_too_large(self):
        """Test form with a file that exceeds size limit."""
        # Create a file larger than 100MB (assuming that's the limit)
        large_content = b"x" * (101 * 1024 * 1024)  # 101 MB
        uploaded_file = SimpleUploadedFile("large.dat", large_content)
        form = FileUploadForm(files={'file': uploaded_file})
        self.assertFalse(form.is_valid())
        self.assertIn('file', form.errors)

    def test_no_file_provided(self):
        """Test form without a file."""
        form = FileUploadForm(files={})
        self.assertFalse(form.is_valid())
        self.assertIn('file', form.errors)

    def test_filename_sanitization(self):
        """Test that filenames are sanitized properly."""
        file_content = b"data"
        # Test with potentially dangerous filename
        uploaded_file = SimpleUploadedFile("../../../etc/passwd.dat", file_content)
        form = FileUploadForm(files={'file': uploaded_file})

        if form.is_valid():
            cleaned_file = form.cleaned_data['file']
            # Should not contain path traversal sequences
            self.assertNotIn('..', cleaned_file.name)
            self.assertNotIn('/', cleaned_file.name)


class ExcelUploadFormTest(TestCase):
    """Tests for ExcelUploadForm."""

    def test_valid_xlsx_file(self):
        """Test form with a valid .xlsx file."""
        file_content = b"PK\x03\x04..."  # Minimal Excel file signature
        uploaded_file = SimpleUploadedFile("test.xlsx", file_content)
        form = ExcelUploadForm(files={'file': uploaded_file})
        self.assertTrue(form.is_valid())

    def test_valid_xls_file(self):
        """Test form with a valid .xls file."""
        file_content = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"  # OLE file signature
        uploaded_file = SimpleUploadedFile("test.xls", file_content)
        form = ExcelUploadForm(files={'file': uploaded_file})
        self.assertTrue(form.is_valid())

    def test_invalid_excel_extension(self):
        """Test form with an invalid file extension for Excel."""
        file_content = b"data"
        # .txt is not in ALLOWED_UPLOAD_EXTENSIONS
        uploaded_file = SimpleUploadedFile("test.txt", file_content)
        form = ExcelUploadForm(files={'file': uploaded_file})
        self.assertFalse(form.is_valid())


class ProjectAnalysisUploadFormTest(TestCase):
    """Tests for ProjectAnalysisUploadForm."""

    def test_valid_two_files(self):
        """Test form with two valid .dat files."""
        budget_file = SimpleUploadedFile("budget.dat", b"budget data")
        plan_file = SimpleUploadedFile("plan.dat", b"plan data")

        form = ProjectAnalysisUploadForm(files={
            'budget_file': budget_file,
            'plan_file': plan_file
        })
        self.assertTrue(form.is_valid())

    def test_missing_budget_file(self):
        """Test form with only plan file."""
        plan_file = SimpleUploadedFile("plan.dat", b"plan data")

        form = ProjectAnalysisUploadForm(files={'plan_file': plan_file})
        self.assertFalse(form.is_valid())
        self.assertIn('budget_file', form.errors)

    def test_missing_plan_file(self):
        """Test form with only budget file."""
        budget_file = SimpleUploadedFile("budget.dat", b"budget data")

        form = ProjectAnalysisUploadForm(files={'budget_file': budget_file})
        self.assertFalse(form.is_valid())
        self.assertIn('plan_file', form.errors)

    def test_invalid_budget_file_extension(self):
        """Test form with invalid budget file extension."""
        budget_file = SimpleUploadedFile("budget.txt", b"budget data")
        plan_file = SimpleUploadedFile("plan.dat", b"plan data")

        form = ProjectAnalysisUploadForm(files={
            'budget_file': budget_file,
            'plan_file': plan_file
        })
        self.assertFalse(form.is_valid())
        self.assertIn('budget_file', form.errors)

    def test_both_files_sanitized(self):
        """Test that both filenames are sanitized."""
        budget_file = SimpleUploadedFile("../budget.dat", b"budget data")
        plan_file = SimpleUploadedFile("../../plan.dat", b"plan data")

        form = ProjectAnalysisUploadForm(files={
            'budget_file': budget_file,
            'plan_file': plan_file
        })

        if form.is_valid():
            budget = form.cleaned_data['budget_file']
            plan = form.cleaned_data['plan_file']

            self.assertNotIn('..', budget.name)
            self.assertNotIn('..', plan.name)
            self.assertEqual(budget.name, 'budget.dat')
            self.assertEqual(plan.name, 'plan.dat')
