import pytest
from django.contrib.auth.models import User
from core.models import Transaction

@pytest.mark.django_db
def test_create_debt_transaction():
    user = User.objects.create_user(username='tester', password='123')
    tx = Transaction.objects.create(
        user=user,
        type='debt',
        category='credit_card',
        amount=500,
        household_type='single'
    )
    assert tx.type == 'debt'
    assert tx.amount == 500

@pytest.mark.django_db
def test_create_loan_transaction():
    user = User.objects.create_user(username='tester', password='123')
    tx = Transaction.objects.create(
        user=user,
        type='loan',
        category='student_loan',
        amount=1000,
        household_type='single'
    )
    assert tx.type == 'loan'
    assert 'loan' in tx.type
