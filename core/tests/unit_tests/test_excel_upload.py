import pandas as pd
from io import BytesIO
from core.models import Transaction
from django.contrib.auth.models import User
import pytest
from datetime import datetime

@pytest.mark.django_db
def test_upload_excel_creates_transactions(client):
    user = User.objects.create_user(username='test', password='123')
    client.login(username='test', password='123')

    # Create test Excel in-memory
    df = pd.DataFrame([{
        'type': 'income',
        'amount': 5000,
        'date': datetime.today().strftime('%Y-%m-%d'),
        'category': 'Freelance',
        'note': 'Test upload'
    }])
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)

    response = client.post(
        '/upload/',  # update to match your URLConf
        {'file': excel_buffer},
        format='multipart'
    )

    assert response.status_code == 302
    assert Transaction.objects.filter(user=user, category='Freelance').exists()



@pytest.mark.django_db
def test_upload_excel_missing_columns(client):
    user = User.objects.create_user(username='test', password='123')
    client.login(username='test', password='123')

    df = pd.DataFrame([{
        'type': 'expense',
        'amount': 1000,
        'date': '2025-07-01',
        # 'category' missing!
    }])
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)

    response = client.post(
        '/upload/',
        {'file': excel_buffer},
        format='multipart'
    )

    assert b"Missing columns" in response.content
