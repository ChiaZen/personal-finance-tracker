# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),  # Homepage view
    path('signup/', views.signup_view, name='signup'),  # Signup view
    path('dashboard/', views.dashboard_view, name='dashboard'), #Dashboard view
    path('add/', views.add_transaction_view, name='add_transaction'),  # Transaction view
]
