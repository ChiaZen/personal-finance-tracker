import pytest
from django.urls import reverse
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_signup_view(client):
    url = reverse('signup')
    response = client.get(url)
    assert response.status_code == 200
    assert 'form' in response.context

    data = {
        'username': 'testuser',
        'password1': 'testpassword123',
        'password2': 'testpassword123'
    }
    response = client.post(url, data)
    assert response.status_code == 302