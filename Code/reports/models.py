from django.db import models

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