from django.forms import ModelForm
from django import forms
from .models import Transaction, Debt, SavingsGoal, PaydayConfig


class TransactionForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ['description', 'amount', 'transaction_type', 'category', 'tag', 'date']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Food, Bills, Transportation'}),
            'tag': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class DebtForm(ModelForm):
    class Meta:
        model = Debt
        fields = ['person_name', 'amount', 'debt_type', 'status', 'date', 'due_date', 'notes']
        widgets = {
            'person_name': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'debt_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class SavingsGoalForm(ModelForm):
    class Meta:
        model = SavingsGoal
        fields = ['goal_name', 'target_amount', 'current_amount', 'deadline']
        widgets = {
            'goal_name': forms.TextInput(attrs={'class': 'form-control'}),
            'target_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'current_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class PaydayConfigForm(ModelForm):
    class Meta:
        model = PaydayConfig
        fields = ['salary_amount']
        widgets = {
            'salary_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }