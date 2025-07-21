import plotly.graph_objs as go
import pandas as pd
from core.models import Transaction
from django.contrib.auth.models import User

def generate_monthly_income_vs_expense(user: User) -> str:
    qs = Transaction.objects.filter(user=user)

    if not qs.exists():
        return "<p>No data for chart.</p>"

    df = pd.DataFrame(list(qs.values('amount', 'type', 'date')))
    df['month'] = pd.to_datetime(df['date']).dt.to_period('M').astype(str)

    summary = (
        df.groupby(['month', 'type'])['amount']
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )

    fig = go.Figure()
    if 'income' in summary.columns:
        fig.add_trace(go.Bar(name='Income', x=summary['month'], y=summary['income']))
    if 'expense' in summary.columns:
        fig.add_trace(go.Bar(name='Expense', x=summary['month'], y=summary['expense']))

    fig.update_layout(
        barmode='group',
        title='Monthly Income vs Expenses',
        xaxis_title='Month',
        yaxis_title='Amount',
        template='plotly_white'
    )

    return fig.to_html(full_html=False)
