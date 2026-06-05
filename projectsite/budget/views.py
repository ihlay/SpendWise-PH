from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q, Sum
from django.utils import timezone

from .models import Transaction, Debt, SavingsGoal, PaydayConfig
from .forms import TransactionForm, DebtForm, SavingsGoalForm

import requests as http_requests 
from datetime import date, timedelta
import calendar
from django.views.generic import TemplateView

from django.db.models import Sum
from django.db.models.functions import ExtractWeekDay
import json as json_module


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


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'budget/transaction_list.html'
    paginate_by = 10

    def get_queryset(self):
        qs = Transaction.objects.filter(user=self.request.user)
        q = self.request.GET.get('q')
        txn_type = self.request.GET.get('type')
        tag = self.request.GET.get('tag')
        if q:
            qs = qs.filter(
                Q(description__icontains=q) |
                Q(category__icontains=q)
            )
        if txn_type in ('income', 'expense'):
            qs = qs.filter(transaction_type=txn_type)
        if tag in ('need', 'want'):
            qs = qs.filter(tag=tag)
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


class DebtListView(LoginRequiredMixin, ListView):
    model = Debt
    template_name = 'budget/debt_list.html'
    context_object_name = 'debts'
    paginate_by = None

    def get_queryset(self):
        return Debt.objects.filter(user=self.request.user).order_by('status', '-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        all_debts = self.get_queryset()
        context['debts_i_owe'] = all_debts.filter(debt_type='i_owe')
        context['debts_owed_to_me'] = all_debts.filter(debt_type='owed_to_me')
        context['total_i_owe'] = all_debts.filter(
            debt_type='i_owe', status__in=['unpaid', 'partial']
        ).aggregate(total=Sum('amount'))['total'] or 0
        context['total_owed_to_me'] = all_debts.filter(
            debt_type='owed_to_me', status__in=['unpaid', 'partial']
        ).aggregate(total=Sum('amount'))['total'] or 0
        return context


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


class DebtMarkPaidView(LoginRequiredMixin, View):
    def post(self, request, pk):
        debt = get_object_or_404(Debt, pk=pk, user=request.user)
        debt.status = 'paid'
        debt.save()
        return redirect('debt-list')


class SavingsGoalListView(LoginRequiredMixin, ListView):
    model = SavingsGoal
    template_name = 'budget/savings_list.html'

    def get_queryset(self):
        return SavingsGoal.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        goals = self.get_queryset()
        context['total_saved'] = goals.aggregate(total=Sum('current_amount'))['total'] or 0
        context['total_target'] = goals.aggregate(total=Sum('target_amount'))['total'] or 0
        return context


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

# Sweldo Tracker view Gawa ni Miko 
class SweldoTrackerView(LoginRequiredMixin, TemplateView):
    template_name = 'budget/sweldo.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        context['today'] = today

        if today.day < 15:
            next_payday = today.replace(day=15)
        elif today.day == 15:
            next_payday = today
        else:
            if today.month == 12:
                next_payday = today.replace(year=today.year + 1, month=1, day=1)
            else:
                next_payday = today.replace(month=today.month + 1, day=1)

        days_until = (next_payday - today).days
        context['next_payday'] = next_payday
        context['days_until_payday'] = days_until
        context['is_payday'] = (days_until == 0)

        if today.day <= 15:
            context['pay_period_label'] = f"1st–15th of {today.strftime('%B')}"
        else:
            last_day = calendar.monthrange(today.year, today.month)[1]
            context['pay_period_label'] = f"16th–{last_day} of {today.strftime('%B')}"

        monthly_expenses = Transaction.objects.filter(
            user=self.request.user,
            transaction_type='expense',
            date__year=today.year,
            date__month=today.month,
        ).aggregate(total=Sum('amount'))['total'] or 0
        context['monthly_expenses'] = monthly_expenses

        try:
            config = PaydayConfig.objects.get(user=self.request.user)
            context['salary'] = config.salary_amount
            if config.salary_amount > 0:
                burn = round((float(monthly_expenses) / float(config.salary_amount)) * 100, 1)
                context['burn_rate'] = min(burn, 100)
            else:
                context['burn_rate'] = 0
        except PaydayConfig.DoesNotExist:
            context['salary'] = None
            context['burn_rate'] = 0

        context['holiday_info'] = self._check_holiday(next_payday)

        ph_holidays = self._get_ph_holidays(today.year)
        context['ph_holidays'] = ph_holidays

        today_str = today.strftime('%Y-%m-%d')
        today_str = today.strftime('%Y-%m-%d')
        context['upcoming_holidays'] = [
            h for h in ph_holidays if h.get('date', '') > today_str
        ]

        return context

    def _check_holiday(self, check_date):
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
        try:
            url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/PH"
            response = http_requests.get(url, timeout=10)
            response.raise_for_status()
            holidays = response.json()
            for h in holidays:
                day = h.get('date', '')[-2:]
                h['is_payday_conflict'] = day in ('01', '15')
            return holidays
        except http_requests.exceptions.RequestException:
            return []
        except (KeyError, ValueError):
            return []

# Analytics view Gawa ni Miko
class AnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'budget/analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = date.today()

        period = self.request.GET.get('period', 'month')
        context['period'] = period

        if period == 'year':
            start_date = date(today.year, 1, 1)
            end_date = date(today.year, 12, 31)
            context['period_label'] = str(today.year)
        else:
            start_date = date(today.year, today.month, 1)
            last_day = calendar.monthrange(today.year, today.month)[1]
            end_date = date(today.year, today.month, last_day)
            context['period_label'] = today.strftime('%B %Y')

        expenses = Transaction.objects.filter(
            user=user,
            transaction_type='expense',
            date__range=(start_date, end_date),
        )

        day_spending = (
            expenses
            .annotate(weekday=ExtractWeekDay('date'))
            .values('weekday')
            .annotate(total=Sum('amount'))
            .order_by('weekday')
        )
        day_names = {1: 'Sun', 2: 'Mon', 3: 'Tue', 4: 'Wed', 5: 'Thu', 6: 'Fri', 7: 'Sat'}
        day_data = {i: 0.0 for i in range(1, 8)}
        for row in day_spending:
            day_data[row['weekday']] = float(row['total'])

        if any(v > 0 for v in day_data.values()):
            top_wd = max(day_data, key=day_data.get)
            context['top_day_name'] = day_names[top_wd]
            context['top_day_amount'] = day_data[top_wd]
        else:
            context['top_day_name'] = None
            context['top_day_amount'] = 0

        context['day_labels_json'] = json_module.dumps(list(day_names.values()))
        context['day_amounts_json'] = json_module.dumps([day_data[i] for i in range(1, 8)])

        cat_spending = (
            expenses.values('category')
            .annotate(total=Sum('amount'))
            .order_by('-total')
        )
        top5 = list(cat_spending[:5])
        context['top_category'] = top5[0]['category'] or 'Uncategorized' if top5 else None
        context['top_category_amount'] = float(top5[0]['total']) if top5 else 0
        context['cat_labels_json'] = json_module.dumps(
            [c['category'] or 'Uncategorized' for c in top5]
        )
        context['cat_amounts_json'] = json_module.dumps(
            [float(c['total']) for c in top5]
        )

        needs = expenses.filter(tag='need').aggregate(total=Sum('amount'))['total'] or 0
        wants = expenses.filter(tag='want').aggregate(total=Sum('amount'))['total'] or 0
        context['needs_total'] = needs
        context['wants_total'] = wants
        context['expense_total'] = needs + wants

        trend_labels, trend_income_data, trend_expense_data = [], [], []
        for i in range(5, -1, -1):
            m, y = today.month - i, today.year
            while m <= 0:
                m += 12
                y -= 1
            inc = Transaction.objects.filter(
                user=user, transaction_type='income',
                date__year=y, date__month=m
            ).aggregate(total=Sum('amount'))['total'] or 0
            exp = Transaction.objects.filter(
                user=user, transaction_type='expense',
                date__year=y, date__month=m
            ).aggregate(total=Sum('amount'))['total'] or 0
            trend_labels.append(date(y, m, 1).strftime('%b %Y'))
            trend_income_data.append(float(inc))
            trend_expense_data.append(float(exp))

        context['trend_labels_json'] = json_module.dumps(trend_labels)
        context['trend_income_json'] = json_module.dumps(trend_income_data)
        context['trend_expense_json'] = json_module.dumps(trend_expense_data)

        return context

