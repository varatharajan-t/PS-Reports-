from django.contrib import admin
from .models import CompanyCode, ProjectType, WBSElement


@admin.register(CompanyCode)
class CompanyCodeAdmin(admin.ModelAdmin):
    """Admin interface for CompanyCode model."""
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    ordering = ('code',)


@admin.register(ProjectType)
class ProjectTypeAdmin(admin.ModelAdmin):
    """Admin interface for ProjectType model."""
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    ordering = ('code',)


@admin.register(WBSElement)
class WBSElementAdmin(admin.ModelAdmin):
    """Admin interface for WBSElement model."""
    list_display = ('wbs_element', 'name')
    search_fields = ('wbs_element', 'name')
    list_per_page = 50
    ordering = ('wbs_element',)
