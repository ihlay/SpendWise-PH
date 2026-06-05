from django.shortcuts import render

from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q, Sum
from django.utils import timezone

from .models import Transaction, Debt, SavingsGoal
from .forms import TransactionForm, DebtForm, SavingsGoalForm

import requests as http_requests 
from datetime import date, timedelta
from django.views.generic import TemplateView

# ── DASHBOARD VIEW ──

class DashboardView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'dashboard.html'
    context_object_name = 'recent_transactions'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-date')[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.now().date()

        month_transactions = Transaction.objects.filter(
            user=user, date__year=today.year, date__month=today.month
        )
        income = month_transactions.filter(transaction_type='income').aggregate(
            total=Sum('amount'))['total'] or 0
        expenses = month_transactions.filter(transaction_type='expense').aggregate(
            total=Sum('amount'))['total'] or 0

        context['total_income'] = income
        context['total_expenses'] = expenses
        context['balance'] = income - expenses

        expense_total = month_transactions.filter(transaction_type='expense')
        wants_total = expense_total.filter(tag='want').aggregate(
            total=Sum('amount'))['total'] or 0
        total_exp_amount = expense_total.aggregate(total=Sum('amount'))['total'] or 1
        context['wants_percentage'] = round((wants_total / total_exp_amount) * 100, 1) if total_exp_amount > 0 else 0

        context['total_debts_i_owe'] = Debt.objects.filter(
            user=user, debt_type='i_owe', status__in=['unpaid', 'partial']
        ).aggregate(total=Sum('amount'))['total'] or 0
        context['total_debts_owed_to_me'] = Debt.objects.filter(
            user=user, debt_type='owed_to_me', status__in=['unpaid', 'partial']
        ).aggregate(total=Sum('amount'))['total'] or 0

        context['active_goals'] = SavingsGoal.objects.filter(user=user).count()
        context['daily_limit'] = self._calculate_daily_limit(user, today, income - expenses)

        return context

    def _calculate_daily_limit(self, user, today, balance):
        day = today.day
        if day < 15:
            next_payday = today.replace(day=15)
        else:
            if today.month == 12:
                next_payday = today.replace(year=today.year + 1, month=1, day=1)
            else:
                next_payday = today.replace(month=today.month + 1, day=1)

        days_left = (next_payday - today).days
        if days_left <= 0:
            days_left = 1
        if balance <= 0:
            return 0
        return round(balance / days_left, 2)


# ── TRANSACTION VIEWS ──

class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'budget/transaction_list.html'
    paginate_by = 10

    def get_queryset(self):
        qs = Transaction.objects.filter(user=self.request.user)
        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(
                Q(description__icontains=query) |
                Q(category__icontains=query)
            )
        return qs

    def get_ordering(self):
        allowed = ['date', '-date', 'amount', '-amount']
        sort_by = self.request.GET.get('sort_by')
        if sort_by in allowed:
            return sort_by
        return '-date'


class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'budget/budget_form.html'
    success_url = reverse_lazy('transaction-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Transaction'
        context['cancel_url'] = reverse_lazy('transaction-list')
        return context


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'budget/budget_form.html'
    success_url = reverse_lazy('transaction-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Transaction'
        context['cancel_url'] = reverse_lazy('transaction-list')
        return context


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    template_name = 'budget/budget_confirm_delete.html'
    success_url = reverse_lazy('transaction-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Transaction'
        context['cancel_url'] = reverse_lazy('transaction-list')
        return context


# ── DEBT VIEWS ──

class DebtListView(LoginRequiredMixin, ListView):
    model = Debt
    template_name = 'budget/debt_list.html'
    paginate_by = 10

    def get_queryset(self):
        qs = Debt.objects.filter(user=self.request.user)
        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(
                Q(person_name__icontains=query) |
                Q(notes__icontains=query)
            )
        return qs

    def get_ordering(self):
        allowed = ['date', '-date', 'amount', '-amount', 'person_name']
        sort_by = self.request.GET.get('sort_by')
        if sort_by in allowed:
            return sort_by
        return '-date'


class DebtCreateView(LoginRequiredMixin, CreateView):
    model = Debt
    form_class = DebtForm
    template_name = 'budget/budget_form.html'
    success_url = reverse_lazy('debt-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Debt'
        context['cancel_url'] = reverse_lazy('debt-list')
        return context


class DebtUpdateView(LoginRequiredMixin, UpdateView):
    model = Debt
    form_class = DebtForm
    template_name = 'budget/budget_form.html'
    success_url = reverse_lazy('debt-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Debt'
        context['cancel_url'] = reverse_lazy('debt-list')
        return context


class DebtDeleteView(LoginRequiredMixin, DeleteView):
    model = Debt
    template_name = 'budget/budget_confirm_delete.html'
    success_url = reverse_lazy('debt-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Debt'
        context['cancel_url'] = reverse_lazy('debt-list')
        return context


# ── SAVINGS GOAL VIEWS ──

class SavingsGoalListView(LoginRequiredMixin, ListView):
    model = SavingsGoal
    template_name = 'budget/savings_list.html'

    def get_queryset(self):
        return SavingsGoal.objects.filter(user=self.request.user)


class SavingsGoalCreateView(LoginRequiredMixin, CreateView):
    model = SavingsGoal
    form_class = SavingsGoalForm
    template_name = 'budget/budget_form.html'
    success_url = reverse_lazy('savings-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Savings Goal'
        context['cancel_url'] = reverse_lazy('savings-list')
        return context


class SavingsGoalUpdateView(LoginRequiredMixin, UpdateView):
    model = SavingsGoal
    form_class = SavingsGoalForm
    template_name = 'budget/budget_form.html'
    success_url = reverse_lazy('savings-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Savings Goal'
        context['cancel_url'] = reverse_lazy('savings-list')
        return context


class SavingsGoalDeleteView(LoginRequiredMixin, DeleteView):
    model = SavingsGoal
    template_name = 'budget/budget_confirm_delete.html'
    success_url = reverse_lazy('savings-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'Savings Goal'
        context['cancel_url'] = reverse_lazy('savings-list')
        return context

# Sweldo Tracker Gawa ni Miko 
class SweldoTrackerView(LoginRequiredMixin, TemplateView):
    template_name = 'budget/sweldo.html'
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
 
        # Determine next payday (1st or 15th)
        if today.day < 15:
            next_payday = today.replace(day=15)
        elif today.day == 15:
            next_payday = today  # today is payday!
        else:
            if today.month == 12:
                next_payday = today.replace(year=today.year + 1, month=1, day=1)
            else:
                next_payday = today.replace(month=today.month + 1, day=1)
 
        days_until = (next_payday - today).days
        context['next_payday'] = next_payday
        context['days_until_payday'] = days_until
        context['is_payday'] = (days_until == 0)
 
        # Check if next payday falls on a holiday using Nager.Date API
        context['holiday_info'] = self._check_holiday(next_payday)
 
        # Get user salary from PaydayConfig
        try:
            config = PaydayConfig.objects.get(user=self.request.user)
            context['salary'] = config.salary_amount
        except PaydayConfig.DoesNotExist:
            context['salary'] = None
 
        # Get list of PH holidays for the current year
        context['ph_holidays'] = self._get_ph_holidays(today.year)
 
        return context
 
    def _check_holiday(self, check_date):
        """Check if a specific date is a Philippine holiday."""
        try:
            url = f"https://date.nager.at/api/v3/PublicHolidays/{check_date.year}/PH"
            response = http_requests.get(url, timeout=10)
            response.raise_for_status()
            holidays = response.json()
 
            date_str = check_date.strftime('%Y-%m-%d')
            for holiday in holidays:
                if holiday['date'] == date_str:
                    return {
                        'is_holiday': True,
                        'name': holiday['localName'],
                        'name_en': holiday['name'],
                    }
            return {'is_holiday': False}
 
        except http_requests.exceptions.RequestException as e:
            return {'is_holiday': False, 'error': str(e)}
        except (KeyError, ValueError):
            return {'is_holiday': False, 'error': 'Could not parse API response'}
 
    def _get_ph_holidays(self, year):
        """Fetch all Philippine holidays for a given year."""
        try:
            url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/PH"
            response = http_requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except http_requests.exceptions.RequestException:
            return []
        except (KeyError, ValueError):
            return []

