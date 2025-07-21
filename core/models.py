from django.db import models
from django.contrib.auth.models import User

class Transaction(models.Model):
    HOUSEHOLD_CHOICES = [
        ('single', 'Single'),
        ('couple', 'Couple'),
        ('family', 'Family'),
    ]

    TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('saving', 'Saving'),
        ('investment', 'Investment'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    category = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    is_recurring = models.BooleanField(default=False)
    household_type = models.CharField(max_length=10, choices=HOUSEHOLD_CHOICES, default='single')

    def __str__(self):
        return f"{self.user.username} | {self.type} | {self.amount:.2f} | {self.category}"


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField()  # used to tie it to time

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    due_date = models.DateField()
    goal_type = models.CharField(max_length=50, choices=[('savings', 'Savings'), ('investment', 'Investment')])
