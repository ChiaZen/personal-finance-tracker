import pytest
from django.contrib.auth.models import User
from core.models import Transaction
from core.charts.income_expenses import generate_monthly_income_vs_expense
from datetime import date

@pytest.mark.django_db
def test_generate_monthly_income_vs_expense():
    user = User.objects.create_user(username='chartuser', password='test')

    Transaction.objects.create(user=user, type='income', category='salary', amount=3000, date=date(2025, 7, 1))
    Transaction.objects.create(user=user, type='expense', category='rent', amount=1000, date=date(2025, 7, 10))

    chart_html = generate_monthly_income_vs_expense(user)

    assert "Monthly Income vs Expenses" in chart_html
    assert "plotly" in chart_html
