from django.urls import path
from . import views
from .views import daily_report, monthly_report

urlpatterns = [
    path('api/products/', views.product_list, name='product_list'),
    path('api/products/create/', views.product_create, name='product_create'),
    path('report/', daily_report, name='daily_report'),
    path('monthly-report/', monthly_report, name='monthly_report'),
    path('monthly-reports/', views.monthly_report_list, name='monthly_report_list'),
    path('permanent-reports/download/', views.download_report_pdf, name='download_permanent_report_pdf'),
]
