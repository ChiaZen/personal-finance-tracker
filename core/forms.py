from django import forms
from .models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['type', 'category', 'amount', 'description', 'is_recurring', 'household_type']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
            'category': forms.TextInput(attrs={'placeholder': 'e.g. Rent, Bitcoin, Groceries'}),
        }


class UploadFileForm(forms.Form):
    file = forms.FileField()