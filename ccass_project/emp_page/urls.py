from django.urls import path,include
from . import views

urlpatterns = [
    path('dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('transactions/', views.transaction_list, name='employee_transactions'),
    path('add-employee/', views.add_employee, name='add_employee'),
    path('products/', views.manage_products, name='manage_products'),
]