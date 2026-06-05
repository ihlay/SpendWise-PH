from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),

    # Transactions
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('transactions/add/', views.TransactionCreateView.as_view(), name='transaction-add'),
    path('transactions/<int:pk>/', views.TransactionUpdateView.as_view(), name='transaction-update'),
    path('transactions/<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction-delete'),

    # Debts
    path('debts/', views.DebtListView.as_view(), name='debt-list'),
    path('debts/add/', views.DebtCreateView.as_view(), name='debt-add'),
    path('debts/<int:pk>/', views.DebtUpdateView.as_view(), name='debt-update'),
    path('debts/<int:pk>/delete/', views.DebtDeleteView.as_view(), name='debt-delete'),

    # Savings Goals
    path('savings/', views.SavingsGoalListView.as_view(), name='savings-list'),
    path('savings/add/', views.SavingsGoalCreateView.as_view(), name='savings-add'),
    path('savings/<int:pk>/', views.SavingsGoalUpdateView.as_view(), name='savings-update'),
    path('savings/<int:pk>/delete/', views.SavingsGoalDeleteView.as_view(), name='savings-delete'),
]