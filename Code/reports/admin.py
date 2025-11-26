from django.contrib import admin
from .models import CompanyCode, ProjectType, WBSElement


@admin.register(CompanyCode)
class CompanyCodeAdmin(admin.ModelAdmin):
    """Admin interface for CompanyCode model with pagination."""
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    ordering = ('code',)
    list_per_page = 25
    show_full_result_count = True
    list_max_show_all = 200


@admin.register(ProjectType)
class ProjectTypeAdmin(admin.ModelAdmin):
    """Admin interface for ProjectType model with pagination."""
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    ordering = ('code',)
    list_per_page = 25
    show_full_result_count = True
    list_max_show_all = 200


@admin.register(WBSElement)
class WBSElementAdmin(admin.ModelAdmin):
    """Admin interface for WBSElement model with enhanced pagination."""
    list_display = ('wbs_element', 'name')
    search_fields = ('wbs_element', 'name')
    list_filter = ('wbs_element',)
    ordering = ('wbs_element',)

    # Pagination settings
    list_per_page = 50  # Show 50 items per page
    show_full_result_count = True  # Show total count
    list_max_show_all = 500  # Maximum items to show on "Show all" page

    # Performance optimization for large datasets
    list_select_related = False  # No foreign keys to optimize

    def get_queryset(self, request):
        """Optimize queryset for large datasets."""
        qs = super().get_queryset(request)
        # Add only() to limit fields if needed for performance
        return qs
