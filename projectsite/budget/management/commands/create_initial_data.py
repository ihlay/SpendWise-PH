from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
from budget.models import Transaction, Debt, SavingsGoal, PaydayConfig
from decimal import Decimal
import random
 
 
class Command(BaseCommand):
    help = 'Create sample data for SpendWise PH'
 
    def handle(self, *args, **kwargs):
        fake = Faker()
 
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created test user: testuser / testpass123'))
 
        # Create Transactions
        categories = ['Food', 'Transportation', 'Bills', 'Shopping', 'Entertainment', 'Health', 'Education']
        tags = ['need', 'want']
        for _ in range(30):
            Transaction.objects.create(
                user=user,
                description=fake.sentence(nb_words=3),
                amount=Decimal(str(round(random.uniform(50, 5000), 2))),
                transaction_type=random.choice(['income', 'expense']),
                category=random.choice(categories),
                tag=random.choice(tags),
                date=fake.date_between(start_date='-60d', end_date='today'),
            )
        self.stdout.write(self.style.SUCCESS('Created 30 sample transactions'))
 
        # Create Debts
        for _ in range(8):
            Debt.objects.create(
                user=user,
                person_name=fake.name(),
                amount=Decimal(str(round(random.uniform(100, 10000), 2))),
                debt_type=random.choice(['i_owe', 'owed_to_me']),
                status=random.choice(['unpaid', 'partial', 'paid']),
                date=fake.date_between(start_date='-90d', end_date='today'),
                due_date=fake.date_between(start_date='today', end_date='+60d'),
                notes=fake.sentence(),
            )
        self.stdout.write(self.style.SUCCESS('Created 8 sample debts'))
 
        # Create Savings Goals
        goals = ['Emergency Fund', 'New Laptop', 'Vacation', 'Gadget Fund', 'House Down Payment']
        for goal_name in goals:
            target = Decimal(str(round(random.uniform(5000, 100000), 2)))
            SavingsGoal.objects.create(
                user=user,
                goal_name=goal_name,
                target_amount=target,
                current_amount=Decimal(str(round(random.uniform(0, float(target)), 2))),
                deadline=fake.date_between(start_date='+30d', end_date='+365d'),
            )
        self.stdout.write(self.style.SUCCESS('Created 5 savings goals'))
 
        # Create PaydayConfig
        PaydayConfig.objects.get_or_create(
            user=user,
            defaults={'salary_amount': Decimal('25000.00')}
        )
        self.stdout.write(self.style.SUCCESS('Created payday config'))
 
        self.stdout.write(self.style.SUCCESS('All sample data created successfully!'))