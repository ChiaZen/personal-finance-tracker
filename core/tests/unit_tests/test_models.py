import pytest
from django.contrib.auth.models import User
from core.models import Transaction

@pytest.mark.django_db
def test_transaction_creation():
    user = User.objects.create_user(username="testuser", password="12345")

    tx = Transaction.objects.create(
        user=user,
        type='income',
        category='salary_after_tax',
        amount=5000.00,
        description='Monthly salary',
        is_recurring=True,
        household_type='single'
    )

    # Assertions
    assert tx.user.username == 'testuser'
    assert tx.type == 'income'
    assert tx.amount == 5000.00
    assert tx.category == 'salary_after_tax'
    assert tx.household_type == 'single'
    assert str(tx) == "testuser | income | 5000.00 | salary_after_tax"


@pytest.mark.django_db
def test_transaction_supports_debt():
    user = User.objects.create_user(username='debtuser', password='pass123')
    tx = Transaction.objects.create(
        user=user,
        type='debt',
        category='credit_card',
        amount=300,
        household_type='single'
    )
    assert tx.type == 'debt'
    assert str(tx) == f"{user.username} | debt | 300.00 | credit_card"
