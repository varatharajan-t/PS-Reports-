"""
Tests for reports app models.
"""
from django.test import TestCase
from django.db import IntegrityError
from reports.models import CompanyCode, ProjectType, WBSElement


class CompanyCodeModelTest(TestCase):
    """Tests for CompanyCode model."""

    def setUp(self):
        """Set up test data."""
        self.company = CompanyCode.objects.create(
            code="1000",
            name="Test Company Ltd"
        )

    def test_company_code_creation(self):
        """Test that a CompanyCode can be created successfully."""
        self.assertEqual(self.company.code, "1000")
        self.assertEqual(self.company.name, "Test Company Ltd")
        self.assertIsNotNone(self.company.pk)  # Has primary key after creation

    def test_company_code_str(self):
        """Test the string representation of CompanyCode."""
        expected = "1000 - Test Company Ltd"
        self.assertEqual(str(self.company), expected)

    def test_company_code_unique_constraint(self):
        """Test that company codes must be unique."""
        with self.assertRaises(IntegrityError):
            CompanyCode.objects.create(
                code="1000",  # Duplicate
                name="Another Company"
            )

    def test_company_code_ordering(self):
        """Test that company codes are ordered by code."""
        CompanyCode.objects.create(code="2000", name="Company B")
        CompanyCode.objects.create(code="1500", name="Company C")

        companies = list(CompanyCode.objects.all())
        self.assertEqual(companies[0].code, "1000")
        self.assertEqual(companies[1].code, "1500")
        self.assertEqual(companies[2].code, "2000")


class ProjectTypeModelTest(TestCase):
    """Tests for ProjectType model."""

    def setUp(self):
        """Set up test data."""
        self.project_type = ProjectType.objects.create(
            code="CAP",
            name="Capital Project"
        )

    def test_project_type_creation(self):
        """Test that a ProjectType can be created successfully."""
        self.assertEqual(self.project_type.code, "CAP")
        self.assertEqual(self.project_type.name, "Capital Project")
        self.assertIsNotNone(self.project_type.pk)  # Has primary key after creation

    def test_project_type_str(self):
        """Test the string representation of ProjectType."""
        expected = "CAP - Capital Project"
        self.assertEqual(str(self.project_type), expected)

    def test_project_type_unique_constraint(self):
        """Test that project type codes must be unique."""
        with self.assertRaises(IntegrityError):
            ProjectType.objects.create(
                code="CAP",  # Duplicate
                name="Another Type"
            )

    def test_project_type_ordering(self):
        """Test that project types are ordered by name."""
        ProjectType.objects.create(code="OM", name="O&M Project")
        ProjectType.objects.create(code="DEV", name="Development")

        types = list(ProjectType.objects.all())
        self.assertEqual(types[0].name, "Capital Project")
        self.assertEqual(types[1].name, "Development")
        self.assertEqual(types[2].name, "O&M Project")


class WBSElementModelTest(TestCase):
    """Tests for WBSElement model."""

    def setUp(self):
        """Set up test data."""
        self.wbs = WBSElement.objects.create(
            wbs_element="P-12345",
            name="Test WBS Element Project"
        )

    def test_wbs_element_creation(self):
        """Test that a WBSElement can be created successfully."""
        self.assertEqual(self.wbs.wbs_element, "P-12345")
        self.assertEqual(self.wbs.name, "Test WBS Element Project")
        self.assertIsNotNone(self.wbs.pk)  # Has primary key after creation

    def test_wbs_element_str(self):
        """Test the string representation of WBSElement."""
        expected = "P-12345"  # Returns only the WBS element code
        self.assertEqual(str(self.wbs), expected)

    def test_wbs_element_unique_constraint(self):
        """Test that WBS elements must be unique."""
        with self.assertRaises(IntegrityError):
            WBSElement.objects.create(
                wbs_element="P-12345",  # Duplicate
                name="Another Project"
            )

    def test_wbs_element_ordering(self):
        """Test that WBS elements are ordered by wbs_element code."""
        WBSElement.objects.create(wbs_element="P-99999", name="Project Z")
        WBSElement.objects.create(wbs_element="P-50000", name="Project M")

        wbs_list = list(WBSElement.objects.all())
        self.assertEqual(wbs_list[0].wbs_element, "P-12345")
        self.assertEqual(wbs_list[1].wbs_element, "P-50000")
        self.assertEqual(wbs_list[2].wbs_element, "P-99999")

    def test_wbs_element_search_by_code(self):
        """Test searching for WBS elements by code."""
        WBSElement.objects.create(wbs_element="P-55555", name="Search Test")

        found = WBSElement.objects.filter(wbs_element__icontains="555")
        self.assertEqual(found.count(), 1)
        self.assertEqual(found.first().wbs_element, "P-55555")

    def test_wbs_element_search_by_name(self):
        """Test searching for WBS elements by name."""
        WBSElement.objects.create(wbs_element="P-77777", name="Unique Project Name")

        found = WBSElement.objects.filter(name__icontains="Unique")
        self.assertEqual(found.count(), 1)
        self.assertEqual(found.first().name, "Unique Project Name")

    def test_bulk_wbs_creation(self):
        """Test creating multiple WBS elements at once."""
        wbs_elements = [
            WBSElement(wbs_element=f"P-{i:05d}", name=f"Project {i}")
            for i in range(1, 101)
        ]
        WBSElement.objects.bulk_create(wbs_elements)

        self.assertEqual(WBSElement.objects.count(), 101)  # 100 + setUp's 1
