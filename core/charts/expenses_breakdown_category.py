import plotly.graph_objs as go
from plotly.offline import plot
from core.models import Transaction

def generate_radar_chart(user):
    # Fetch expenses only
    transactions = Transaction.objects.filter(user=user, type='expense')
    
    if not transactions.exists():
        return "<p>No data for radar chart.</p>"

    # Group by category
    category_totals = {}
    for tx in transactions:
        category_totals[tx.category] = category_totals.get(tx.category, 0) + tx.amount

    labels = list(category_totals.keys())
    values = list(category_totals.values())

    # Close the radar loop
    labels.append(labels[0])
    values.append(values[0])

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=labels,
        fill='toself',
        name='Expense Categories',
        marker=dict(color='rgba(0,123,255,0.7)')
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max(values) * 1.2])
        ),
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=20),
        height=400,
        title="Radar: Expense by Category"
    )

    return plot(fig, output_type='div')
