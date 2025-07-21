from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'category', 'amount', 'date', 'household_type', 'is_recurring')
    list_filter = ('type', 'household_type', 'is_recurring', 'date')
    search_fields = ('user__username', 'category', 'description')
