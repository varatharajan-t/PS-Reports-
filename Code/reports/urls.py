from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('report/budget/', views.budget_report_view, name='report_budget'),
    path('report/budget-updates/', views.budget_updates_report_view, name='report_budget_updates'),
    path('report/budget-variance/', views.budget_variance_report_view, name='report_budget_variance'),
    path('report/project-type-wise/', views.project_type_wise_report_view, name='report_project_type_wise'),
    path('report/glimps-of-projects/', views.glimps_of_projects_report_view, name='report_glimps_of_projects'),
    path('report/plan-variance/', views.plan_variance_report_view, name='report_plan_variance'),
    path('report/project-analysis/', views.project_analysis_report_view, name='report_project_analysis'),
    path('download/<str:filename>/', views.download_report_view, name='download_report'),
]
