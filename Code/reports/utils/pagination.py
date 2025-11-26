"""
Pagination utilities for handling large datasets efficiently.
"""
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from typing import Any, Dict, Optional


# Default pagination settings
DEFAULT_PAGE_SIZE = getattr(settings, 'DEFAULT_PAGE_SIZE', 25)
MAX_PAGE_SIZE = getattr(settings, 'MAX_PAGE_SIZE', 100)


def paginate_queryset(queryset, page_number: int = 1, page_size: Optional[int] = None) -> Dict[str, Any]:
    """
    Paginate a Django queryset efficiently.

    Args:
        queryset: Django queryset to paginate
        page_number: Page number to retrieve (1-indexed)
        page_size: Number of items per page (default: DEFAULT_PAGE_SIZE)

    Returns:
        Dictionary containing:
            - page_obj: Paginated page object
            - paginator: Paginator instance
            - is_paginated: Boolean indicating if pagination is applied
            - page_range: Range of page numbers to display

    Example:
        >>> from reports.models import WBSElement
        >>> queryset = WBSElement.objects.all()
        >>> result = paginate_queryset(queryset, page_number=2, page_size=50)
        >>> for item in result['page_obj']:
        >>>     print(item)
    """
    if page_size is None:
        page_size = DEFAULT_PAGE_SIZE

    # Enforce maximum page size
    page_size = min(page_size, MAX_PAGE_SIZE)

    # Create paginator
    paginator = Paginator(queryset, page_size)

    # Get the requested page
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        page_obj = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        page_obj = paginator.page(paginator.num_pages)

    # Calculate page range for pagination display (show 5 pages at a time)
    current_page = page_obj.number
    total_pages = paginator.num_pages

    # Show 5 page numbers: 2 before, current, 2 after
    page_range_start = max(1, current_page - 2)
    page_range_end = min(total_pages, current_page + 2)

    # Adjust if we're near the beginning or end
    if current_page <= 3:
        page_range_end = min(5, total_pages)
    if current_page >= total_pages - 2:
        page_range_start = max(1, total_pages - 4)

    page_range = range(page_range_start, page_range_end + 1)

    return {
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': paginator.num_pages > 1,
        'page_range': page_range,
        'total_count': paginator.count,
        'page_size': page_size,
    }


def paginate_list(items: list, page_number: int = 1, page_size: Optional[int] = None) -> Dict[str, Any]:
    """
    Paginate a Python list.

    Args:
        items: List of items to paginate
        page_number: Page number to retrieve (1-indexed)
        page_size: Number of items per page

    Returns:
        Dictionary with pagination information

    Example:
        >>> items = list(range(100))
        >>> result = paginate_list(items, page_number=3, page_size=10)
        >>> print(result['page_obj'].object_list)  # Items 20-29
    """
    if page_size is None:
        page_size = DEFAULT_PAGE_SIZE

    page_size = min(page_size, MAX_PAGE_SIZE)

    paginator = Paginator(items, page_size)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return {
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': paginator.num_pages > 1,
        'total_count': len(items),
    }


class PaginationMixin:
    """
    Mixin for class-based views to add pagination support.

    Usage:
        class MyListView(PaginationMixin, ListView):
            model = MyModel
            paginate_by = 25
    """
    paginate_by = DEFAULT_PAGE_SIZE
    paginate_orphans = 5  # Include last few items on previous page if < this number

    def get_paginate_by(self, queryset):
        """
        Get the number of items to paginate by.
        Can be overridden to get from request parameters.
        """
        # Allow page_size to be specified in URL parameters
        page_size = self.request.GET.get('page_size')
        if page_size:
            try:
                page_size = int(page_size)
                return min(page_size, MAX_PAGE_SIZE)
            except ValueError:
                pass
        return self.paginate_by


def get_pagination_context(page_obj, paginator) -> Dict[str, Any]:
    """
    Generate template context for pagination.

    Args:
        page_obj: Page object from Paginator
        paginator: Paginator instance

    Returns:
        Dictionary with pagination context variables

    Example in template:
        {% if is_paginated %}
            <nav>
                {% if page_obj.has_previous %}
                    <a href="?page={{ page_obj.previous_page_number }}">Previous</a>
                {% endif %}
                <span>Page {{ page_obj.number }} of {{ paginator.num_pages }}</span>
                {% if page_obj.has_next %}
                    <a href="?page={{ page_obj.next_page_number }}">Next</a>
                {% endif %}
            </nav>
        {% endif %}
    """
    return {
        'is_paginated': paginator.num_pages > 1,
        'page_obj': page_obj,
        'paginator': paginator,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number,
        'total_count': paginator.count,
        'start_index': page_obj.start_index(),
        'end_index': page_obj.end_index(),
    }


def chunk_queryset(queryset, chunk_size: int = 1000):
    """
    Generator to process large querysets in chunks.
    Useful for batch processing without loading all data into memory.

    Args:
        queryset: Django queryset to chunk
        chunk_size: Number of items per chunk

    Yields:
        Chunks of the queryset

    Example:
        >>> from reports.models import WBSElement
        >>> queryset = WBSElement.objects.all()
        >>> for chunk in chunk_queryset(queryset, chunk_size=500):
        >>>     for item in chunk:
        >>>         process(item)
    """
    start = 0
    while True:
        chunk = queryset[start:start + chunk_size]
        if not chunk:
            break
        yield chunk
        start += chunk_size
