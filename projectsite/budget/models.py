from django.db import models
from django.contrib.auth.models import User
 
 
class BaseModel(models.Model):
    """Abstract base model with timestamps for all models."""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    class Meta:
        abstract = True
 
 
class Transaction(BaseModel):
    """Tracks daily income and expenses."""
    TRANSACTION_TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    TAG_CHOICES = [
        ('need', 'Need'),
        ('want', 'Want'),
    ]
 
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    category = models.CharField(max_length=100, blank=True)
    tag = models.CharField(max_length=10, choices=TAG_CHOICES, default='need')
    date = models.DateField()
 
    def __str__(self):
        return f"{self.description} - {self.amount}"
 
    class Meta:
        ordering = ['-date']
 
 
class Debt(BaseModel):
    """Tracks money owed (utang) - both what I owe and what others owe me."""
    DEBT_TYPE_CHOICES = [
        ('i_owe', 'I Owe (Utang Ko)'),
        ('owed_to_me', 'Owed to Me (Utang Sa Akin)'),
    ]
    STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
    ]
 
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='debts')
    person_name = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    debt_type = models.CharField(max_length=15, choices=DEBT_TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unpaid')
    date = models.DateField()
    due_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)
 
    def __str__(self):
        return f"{self.person_name} - PHP {self.amount} ({self.get_debt_type_display()})"
 
    class Meta:
        ordering = ['-date']
 
 
class SavingsGoal(BaseModel):
    """Tracks savings goals with progress."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='savings_goals')
    goal_name = models.CharField(max_length=200)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deadline = models.DateField(blank=True, null=True)
 
    @property
    def progress_percentage(self):
        if self.target_amount > 0:
            return round((self.current_amount / self.target_amount) * 100, 1)
        return 0
 
    def __str__(self):
        return f"{self.goal_name} - {self.progress_percentage}%"
 
    class Meta:
        ordering = ['deadline']
 
 
class PaydayConfig(BaseModel):
    """Stores user's salary configuration for Sweldo Tracker."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='payday_config')
    salary_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
 
    def __str__(self):
        return f"{self.user.username} - PHP {self.salary_amount}"
