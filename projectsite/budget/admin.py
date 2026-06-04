from django.contrib import admin
from .models import Transaction, Debt, SavingsGoal, PaydayConfig
 
 
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('description', 'amount', 'transaction_type', 'tag', 'category', 'date', 'user')
    search_fields = ('description', 'category')
    list_filter = ('transaction_type', 'tag', 'date')
 
 
@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ('person_name', 'amount', 'debt_type', 'status', 'date', 'due_date', 'user')
    search_fields = ('person_name', 'notes')
    list_filter = ('debt_type', 'status')
 
 
@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ('goal_name', 'target_amount', 'current_amount', 'progress_percentage', 'deadline', 'user')
    search_fields = ('goal_name',)
 
    def progress_percentage(self, obj):
        return f"{obj.progress_percentage}%"
    progress_percentage.short_description = 'Progress'
 
 
@admin.register(PaydayConfig)
class PaydayConfigAdmin(admin.ModelAdmin):
    list_display = ('user', 'salary_amount')
