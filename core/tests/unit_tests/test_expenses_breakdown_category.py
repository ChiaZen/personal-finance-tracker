import pytest
from core.models import Transaction
from core.charts.expenses_breakdown_category import generate_radar_chart
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_generate_radar_chart_returns_plotly_html():
    user = User.objects.create_user(username='radar', password='test123')

    Transaction.objects.create(user=user, type='expense', category='Food', amount=200)
    Transaction.objects.create(user=user, type='expense', category='Rent', amount=800)
    Transaction.objects.create(user=user, type='expense', category='Transport', amount=150)

    html = generate_radar_chart(user)
    assert '<div' in html and 'plotly' in html
