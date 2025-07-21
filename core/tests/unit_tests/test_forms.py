import pytest
from django.contrib.auth.forms import UserCreationForm

@pytest.mark.django_db
def test_user_creation_form_valid():
    form = UserCreationForm(data={
        'username': 'myuser',
        'password1': 'StrongPass123',
        'password2': 'StrongPass123'
    })
    assert form.is_valid()


@pytest.mark.django_db
def test_user_creation_form_password_mismatch():
    form = UserCreationForm(data={
        'username': 'myuser',
        'password1': 'onepass',
        'password2': 'twopass'
    })
    assert not form.is_valid()
    assert 'password2' in form.errors
