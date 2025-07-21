from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from core.models import Transaction
from django.db.models import Sum
import plotly.graph_objs as go
from plotly.offline import plot

def home_view(request):
    return render(request, 'home.html')  

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # redirect to login after signup
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def generate_pie_chart(transactions):
    category_totals = {}
    for tx in transactions:
        if tx.type == 'expense':
            category_totals[tx.category] = category_totals.get(tx.category, 0) + tx.amount

    labels = list(category_totals.keys())
    values = list(category_totals.values())

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4)])
    fig.update_layout(title='Expense Breakdown by Category')
    return plot(fig, output_type='div')

@login_required
def dashboard_view(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user).order_by('-date')[:50]

    totals = Transaction.objects.filter(user=user).values('type').annotate(total=Sum('amount'))
    summary = {t['type']: t['total'] for t in totals}

    pie_chart = generate_pie_chart(transactions)

    context = {
        'transactions': transactions,
        'summary': {
            'income': summary.get('income', 0),
            'expense': summary.get('expense', 0),
            'saving': summary.get('saving', 0),
            'investment': summary.get('investment', 0),
        },
        'pie_chart': pie_chart,
    }
    return render(request, 'dashboard.html', context)


from .forms import TransactionForm

@login_required
def add_transaction_view(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            tx = form.save(commit=False)
            tx.user = request.user  # tie transaction to logged-in user
            tx.save()
            return redirect('dashboard')
    else:
        form = TransactionForm()

    return render(request, 'add_transaction.html', {'form': form})
