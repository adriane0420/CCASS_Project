from django.urls import path,include
from . import views

urlpatterns = [
     path('dashboard/', views.client_dashboard, name='client_dashboard'),
     path('transaction/', views.pallet_transaction, name='pallet-transaction'),
     path('confirm-payment/', views.confirm_payment, name='confirm-payment'),
]