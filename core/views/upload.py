import pandas as pd
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.forms import UploadFileForm
from core.models import Transaction
from datetime import datetime

@login_required
def upload_excel_view(request):
    message = ''
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            try:
                df = pd.read_excel(excel_file)

                required_columns = {'type', 'amount', 'date', 'category'}
                if not required_columns.issubset(df.columns):
                    message = f"Missing columns. Required: {required_columns}"
                else:
                    for _, row in df.iterrows():
                        Transaction.objects.create(
                            user=request.user,
                            type=row['type'].lower(),
                            amount=row['amount'],
                            date=pd.to_datetime(row['date']),
                            category=row['category'],
                            note=row.get('note', '')
                        )
                    return redirect('dashboard')
            except Exception as e:
                message = f"Upload failed: {str(e)}"
    else:
        form = UploadFileForm()

    return render(request, 'upload.html', {'form': form, 'message': message})
