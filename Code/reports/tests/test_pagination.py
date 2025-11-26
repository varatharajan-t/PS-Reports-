"""
Tests for pagination utilities.
"""
from django.test import TestCase, Client
from django.urls import reverse
from reports.models import WBSElement, CompanyCode, ProjectType
from reports.utils.pagination import (
    paginate_queryset,
    paginate_list,
    get_pagination_context,
    chunk_queryset,
    PaginationMixin,
)


class PaginateQuerysetTest(TestCase):
    """Tests for paginate_queryset function."""

    @classmethod
    def setUpTestData(cls):
        """Create test WBS elements."""
        # Create 100 WBS elements
        WBSElement.objects.bulk_create([
            WBSElement(wbs_element=f"P-{i:05d}", name=f"Project {i}")
            for i in range(100)
        ])

    def test_paginate_first_page(self):
        """Test paginating first page."""
        queryset = WBSElement.objects.all()
        result = paginate_queryset(queryset, page_number=1, page_size=25)

        self.assertEqual(result['page_obj'].number, 1)
        self.assertEqual(len(result['page_obj']), 25)
        self.assertEqual(result['total_count'], 100)
        self.assertTrue(result['is_paginated'])

    def test_paginate_last_page(self):
        """Test paginating last page."""
        queryset = WBSElement.objects.all()
        result = paginate_queryset(queryset, page_number=4, page_size=25)

        self.assertEqual(result['page_obj'].number, 4)
        self.assertEqual(len(result['page_obj']), 25)

    def test_paginate_invalid_page_number(self):
        """Test with invalid page number."""
        queryset = WBSElement.objects.all()
        result = paginate_queryset(queryset, page_number='invalid', page_size=25)

        # Should default to first page
        self.assertEqual(result['page_obj'].number, 1)

    def test_paginate_out_of_range(self):
        """Test page number out of range."""
        queryset = WBSElement.objects.all()
        result = paginate_queryset(queryset, page_number=999, page_size=25)

        # Should return last page
        self.assertEqual(result['page_obj'].number, 4)

    def test_page_range_calculation(self):
        """Test that page range is calculated correctly."""
        queryset = WBSElement.objects.all()
        result = paginate_queryset(queryset, page_number=2, page_size=20)

        # Should return range around current page
        self.assertIn('page_range', result)
        self.assertIsInstance(result['page_range'], range)

    def test_custom_page_size(self):
        """Test with custom page size."""
        queryset = WBSElement.objects.all()
        result = paginate_queryset(queryset, page_number=1, page_size=50)

        self.assertEqual(len(result['page_obj']), 50)
        self.assertEqual(result['page_size'], 50)

    def test_max_page_size_enforcement(self):
        """Test that max page size is enforced."""
        queryset = WBSElement.objects.all()
        result = paginate_queryset(queryset, page_number=1, page_size=500)

        # Should cap at MAX_PAGE_SIZE (100)
        self.assertLessEqual(result['page_size'], 100)


class PaginateListTest(TestCase):
    """Tests for paginate_list function."""

    def test_paginate_simple_list(self):
        """Test paginating a simple list."""
        items = list(range(50))
        result = paginate_list(items, page_number=1, page_size=10)

        self.assertEqual(len(result['page_obj'].object_list), 10)
        self.assertEqual(result['total_count'], 50)
        self.assertTrue(result['is_paginated'])

    def test_paginate_empty_list(self):
        """Test paginating an empty list."""
        items = []
        result = paginate_list(items, page_number=1, page_size=10)

        self.assertEqual(len(result['page_obj'].object_list), 0)
        self.assertFalse(result['is_paginated'])

    def test_paginate_list_second_page(self):
        """Test getting second page."""
        items = list(range(100))
        result = paginate_list(items, page_number=2, page_size=25)

        self.assertEqual(result['page_obj'].number, 2)
        # Items 25-49
        self.assertEqual(result['page_obj'].object_list[0], 25)


class GetPaginationContextTest(TestCase):
    """Tests for get_pagination_context function."""

    @classmethod
    def setUpTestData(cls):
        """Create test data."""
        WBSElement.objects.bulk_create([
            WBSElement(wbs_element=f"P-{i:05d}", name=f"Project {i}")
            for i in range(50)
        ])

    def test_pagination_context_structure(self):
        """Test that context has all required keys."""
        queryset = WBSElement.objects.all()
        result = paginate_queryset(queryset, page_number=2, page_size=10)

        context = get_pagination_context(
            result['page_obj'],
            result['paginator']
        )

        required_keys = [
            'is_paginated', 'page_obj', 'paginator',
            'has_previous', 'has_next',
            'previous_page_number', 'next_page_number',
            'total_pages', 'current_page', 'total_count',
            'start_index', 'end_index'
        ]

        for key in required_keys:
            self.assertIn(key, context)

    def test_context_has_previous(self):
        """Test has_previous flag."""
        queryset = WBSElement.objects.all()
        result = paginate_queryset(queryset, page_number=2, page_size=10)
        context = get_pagination_context(result['page_obj'], result['paginator'])

        self.assertTrue(context['has_previous'])
        self.assertEqual(context['previous_page_number'], 1)

    def test_context_has_next(self):
        """Test has_next flag."""
        queryset = WBSElement.objects.all()
        result = paginate_queryset(queryset, page_number=1, page_size=10)
        context = get_pagination_context(result['page_obj'], result['paginator'])

        self.assertTrue(context['has_next'])
        self.assertEqual(context['next_page_number'], 2)


class ChunkQuerysetTest(TestCase):
    """Tests for chunk_queryset generator."""

    @classmethod
    def setUpTestData(cls):
        """Create test data."""
        WBSElement.objects.bulk_create([
            WBSElement(wbs_element=f"P-{i:05d}", name=f"Project {i}")
            for i in range(100)
        ])

    def test_chunk_queryset_basic(self):
        """Test basic chunking."""
        queryset = WBSElement.objects.all()
        chunks = list(chunk_queryset(queryset, chunk_size=25))

        self.assertEqual(len(chunks), 4)
        self.assertEqual(len(chunks[0]), 25)

    def test_chunk_queryset_uneven(self):
        """Test chunking with uneven division."""
        queryset = WBSElement.objects.all()[:95]  # 95 items
        chunks = list(chunk_queryset(queryset, chunk_size=30))

        self.assertEqual(len(chunks), 4)
        # Last chunk should have 5 items (95 % 30 = 5)
        self.assertEqual(len(chunks[-1]), 5)

    def test_chunk_empty_queryset(self):
        """Test chunking empty queryset."""
        queryset = WBSElement.objects.filter(wbs_element="NONEXISTENT")
        chunks = list(chunk_queryset(queryset, chunk_size=10))

        self.assertEqual(len(chunks), 0)


class BrowseViewsTest(TestCase):
    """Tests for pagination in browse views."""

    @classmethod
    def setUpTestData(cls):
        """Create test data."""
        # Create WBS elements
        WBSElement.objects.bulk_create([
            WBSElement(wbs_element=f"P-{i:05d}", name=f"Project {i}")
            for i in range(75)
        ])

        # Create company codes
        CompanyCode.objects.bulk_create([
            CompanyCode(code=f"CC{i:02d}", name=f"Company {i}")
            for i in range(10)
        ])

        # Create project types
        ProjectType.objects.bulk_create([
            ProjectType(code=f"PT{i}", name=f"Type {i}")
            for i in range(5)
        ])

    def setUp(self):
        """Set up test client."""
        self.client = Client()

    def test_browse_wbs_view_status_code(self):
        """Test that browse WBS view loads successfully."""
        response = self.client.get(reverse('browse_wbs'))
        self.assertEqual(response.status_code, 200)

    def test_browse_wbs_pagination(self):
        """Test WBS pagination."""
        response = self.client.get(reverse('browse_wbs') + '?page=2')
        self.assertEqual(response.status_code, 200)

        # Check pagination context
        self.assertIn('page_obj', response.context)
        self.assertIn('is_paginated', response.context)
        self.assertTrue(response.context['is_paginated'])

    def test_browse_wbs_search(self):
        """Test WBS search functionality."""
        response = self.client.get(reverse('browse_wbs') + '?search=P-00001')
        self.assertEqual(response.status_code, 200)

        # Should have search results
        self.assertIn('search_query', response.context)
        self.assertEqual(response.context['search_query'], 'P-00001')

    def test_browse_wbs_page_size(self):
        """Test custom page size."""
        response = self.client.get(reverse('browse_wbs') + '?page_size=25')
        self.assertEqual(response.status_code, 200)

        # Check page size
        self.assertEqual(response.context['page_size'], 25)

    def test_browse_master_data_view(self):
        """Test browse master data view."""
        response = self.client.get(reverse('browse_master_data'))
        self.assertEqual(response.status_code, 200)

    def test_browse_master_data_types(self):
        """Test switching between data types."""
        # Test WBS
        response = self.client.get(reverse('browse_master_data') + '?type=wbs')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['data_type'], 'wbs')

        # Test company codes
        response = self.client.get(reverse('browse_master_data') + '?type=company_codes')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['data_type'], 'company_codes')

        # Test project types
        response = self.client.get(reverse('browse_master_data') + '?type=project_types')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['data_type'], 'project_types')

    def test_pagination_template_rendering(self):
        """Test that pagination template renders correctly."""
        response = self.client.get(reverse('browse_wbs'))
        self.assertContains(response, 'pagination')
        self.assertContains(response, 'page-item')


class PaginationMixinTest(TestCase):
    """Tests for PaginationMixin class."""

    def test_mixin_has_default_paginate_by(self):
        """Test that mixin has default paginate_by."""
        mixin = PaginationMixin()
        self.assertIsNotNone(mixin.paginate_by)

    def test_mixin_has_paginate_orphans(self):
        """Test that mixin has paginate_orphans."""
        mixin = PaginationMixin()
        self.assertIsNotNone(mixin.paginate_orphans)
