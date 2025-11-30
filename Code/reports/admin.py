from django.contrib import admin
from .models import CompanyCode, ProjectType, WBSElement, ReportHistory


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


@admin.register(ReportHistory)
class ReportHistoryAdmin(admin.ModelAdmin):
    """Admin interface for ReportHistory model."""
    list_display = (
        'report_type',
        'filename',
        'user',
        'file_size_display',
        'status',
        'created_at',
        'rows_processed'
    )
    list_filter = ('report_type', 'status', 'created_at', 'user')
    search_fields = ('filename', 'user__username', 'error_message')
    readonly_fields = (
        'user',
        'report_type',
        'filename',
        'file_path',
        'file_size',
        'status',
        'error_message',
        'created_at',
        'rows_processed',
        'file_exists_display'
    )
    ordering = ('-created_at',)
    list_per_page = 50
    date_hierarchy = 'created_at'

    def file_size_display(self, obj):
        """Display file size in MB."""
        return f"{obj.file_size_mb} MB"
    file_size_display.short_description = 'File Size'

    def file_exists_display(self, obj):
        """Display if file exists."""
        return "✓ Yes" if obj.file_exists else "✗ No"
    file_exists_display.short_description = 'File Exists'

    def has_add_permission(self, request):
        """Prevent manual addition of report history."""
        return False

    def has_change_permission(self, request, obj=None):
        """Prevent modification of report history."""
        return False
