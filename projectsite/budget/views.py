from django.shortcuts import render

# Create your views here.

from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q

from .models import Transaction, Debt, SavingsGoal
from .forms import TransactionForm, DebtForm, SavingsGoalForm


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