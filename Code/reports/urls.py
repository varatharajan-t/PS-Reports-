from django.urls import path
from . import views
from . import views_auth

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Authentication URLs
    path('accounts/login/', views_auth.login_view, name='login'),
    path('accounts/logout/', views_auth.logout_view, name='logout'),
    path('accounts/register/', views_auth.register_view, name='register'),
    path('accounts/profile/', views_auth.profile_view, name='profile'),
    path('accounts/change-password/', views_auth.change_password_view, name='change_password'),

    # Report URLs
    path('report/budget/', views.budget_report_view, name='report_budget'),
    path('report/budget-updates/', views.budget_updates_report_view, name='report_budget_updates'),
    path('report/budget-variance/', views.budget_variance_report_view, name='report_budget_variance'),
    path('report/project-type-wise/', views.project_type_wise_report_view, name='report_project_type_wise'),
    path('report/glimps-of-projects/', views.glimps_of_projects_report_view, name='report_glimps_of_projects'),
    path('report/plan-variance/', views.plan_variance_report_view, name='report_plan_variance'),
    path('report/project-analysis/', views.project_analysis_report_view, name='report_project_analysis'),
    path('download/<str:filename>/', views.download_report_view, name='download_report'),

    # Master Data Browsing with Pagination
    path('browse/wbs/', views.browse_wbs_elements, name='browse_wbs'),
    path('browse/master-data/', views.browse_master_data, name='browse_master_data'),
]
