# core/urls.py
from django.urls import path
from core.views.auth import home_view, signup_view
from core.views.transaction import add_transaction_view
from core.views.dashboard import dashboard_view
from core.views.upload import upload_excel_view

urlpatterns = [
    path('', home_view, name='home'),  # Homepage view
    path('signup/', signup_view, name='signup'),  # Signup view
    path('dashboard/', dashboard_view, name='dashboard'), #Dashboard view
    path('add/', add_transaction_view, name='add_transaction'),  # Transaction view
    path('upload/', upload_excel_view, name='upload_excel'), #Upload the excel file view
]
