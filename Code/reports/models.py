from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os


class CompanyCode(models.Model):
    """Represents a company code, e.g., NL for NLCIL."""
    code = models.CharField(max_length=10, unique=True, help_text="The short code for the company (e.g., 'NL').")
    name = models.CharField(max_length=255, help_text="The full name of the company (e.g., 'NLCIL').")

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = "Company Code"
        verbose_name_plural = "Company Codes"
        ordering = ['code']


class ProjectType(models.Model):
    """Represents a project type, e.g., S for Service."""
    code = models.CharField(max_length=10, unique=True, help_text="The short code for the project type (e.g., 'S').")
    name = models.CharField(max_length=255, help_text="The full name of the project type (e.g., 'Service').")

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = "Project Type"
        verbose_name_plural = "Project Types"
        ordering = ['code']


class WBSElement(models.Model):
    """
    Represents a Work Breakdown Structure (WBS) element.
    This model stores the master data mapping WBS element IDs to their names/descriptions.
    """
    wbs_element = models.CharField(max_length=255, unique=True, db_index=True, help_text="The unique identifier for the WBS element.")
    name = models.CharField(max_length=255, help_text="The descriptive name of the WBS element.")
    
    def __str__(self):
        return self.wbs_element

    class Meta:
        verbose_name = "WBS Element"
        verbose_name_plural = "WBS Elements"
        ordering = ['wbs_element']


class ReportHistory(models.Model):
    """
    Tracks generated reports for audit trail and re-download capability.
    """
    REPORT_TYPES = [
        ('budget', 'Budget Report'),
        ('budget_updates', 'Budget Updates'),
        ('budget_variance', 'Budget Variance'),
        ('project_type_wise', 'Project Type Wise'),
        ('glimps_of_projects', 'Glimps of Projects'),
        ('plan_variance', 'Plan Variance'),
        ('project_analysis', 'Project Analysis'),
    ]

    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('processing', 'Processing'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who generated the report"
    )
    report_type = models.CharField(
        max_length=50,
        choices=REPORT_TYPES,
        help_text="Type of report generated"
    )
    filename = models.CharField(
        max_length=255,
        help_text="Name of the generated file"
    )
    file_path = models.CharField(
        max_length=500,
        help_text="Full path to the generated file"
    )
    file_size = models.BigIntegerField(
        default=0,
        help_text="Size of the file in bytes"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='success',
        help_text="Status of report generation"
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        help_text="Error message if generation failed"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the report was generated"
    )
    rows_processed = models.IntegerField(
        default=0,
        help_text="Number of data rows processed"
    )

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.filename} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    @property
    def file_size_mb(self):
        """Return file size in megabytes."""
        return round(self.file_size / (1024 * 1024), 2)

    @property
    def file_exists(self):
        """Check if the file still exists on disk."""
        return os.path.exists(self.file_path) if self.file_path else False

    class Meta:
        verbose_name = "Report History"
        verbose_name_plural = "Report Histories"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['report_type', '-created_at']),
        ]