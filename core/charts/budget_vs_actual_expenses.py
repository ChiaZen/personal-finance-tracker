import plotly.graph_objects as go
from plotly.offline import plot
import pandas as pd
import duckdb

def generate_budget_vs_actual_chart(username_or_df):
    """Generate budget vs actual chart - accepts either username or DataFrame"""
    
    # If a string is passed, fetch data from database
    if isinstance(username_or_df, str):
        username = username_or_df
        con = duckdb.connect("db/finance.duckdb")
        
        query = """
        SELECT 
            ue.month,
            e.category,
            SUM(ue.budget_amount) as budget_amount,
            SUM(ue.actual_amount) as actual_amount
        FROM user_expenses ue
        JOIN users u ON ue.user_id = u.id
        JOIN expenses e ON ue.expenses_id = e.id
        WHERE u.username = ? AND ue.year = 2025
        GROUP BY ue.month, e.category
        ORDER BY ue.month, e.category
        """
        
        try:
            df = con.execute(query, [username]).fetchdf()
            con.close()
            
            if df.empty:
                return "<div><p>No budget vs actual data available for this user.</p></div>"
                
        except Exception as e:
            con.close()
            return f"<div><p>Error generating budget vs actual chart: {str(e)}</p></div>"
    else:
        # DataFrame was passed directly
        df = username_or_df

    # Check if required columns exist
    required_cols = ['month', 'category', 'budget_amount', 'actual_amount']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        return f"<div><p>Missing columns in data: {missing_cols}</p></div>"

    # Group data by month and category
    grouped = df.groupby(['month', 'category'])[['budget_amount', 'actual_amount']].sum().reset_index()

    fig = go.Figure()
    
    # Get unique categories and months for better organization
    categories = grouped['category'].unique()
    months = sorted(grouped['month'].unique())
    
    # Create grouped bar chart
    for category in categories:
        category_df = grouped[grouped['category'] == category]
        
        # Budget bars
        fig.add_trace(go.Bar(
            x=[f"{month}" for month in category_df['month']],
            y=category_df['budget_amount'],
            name=f'{category.title()} Budget',
            marker_color='lightblue',
            offsetgroup=category,
            legendgroup=category
        ))
        
        # Actual bars
        fig.add_trace(go.Bar(
            x=[f"{month}" for month in category_df['month']],
            y=category_df['actual_amount'],
            name=f'{category.title()} Actual',
            marker_color='orange',
            offsetgroup=category,
            legendgroup=category
        ))

    fig.update_layout(
        barmode='group',
        xaxis_title='Month',
        yaxis_title='Amount (DKK)',
        template='plotly_white',
        height=500,
        margin=dict(t=60, b=50, l=50, r=50),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )

    return plot(fig, output_type='div')

def generate_monthly_variance_chart(username):
    """Generate a chart showing budget variance (over/under budget) by month"""
    con = duckdb.connect("db/finance.duckdb")
    
    query = """
    SELECT 
        ue.month,
        e.category,
        SUM(ue.budget_amount) as budget_amount,
        SUM(ue.actual_amount) as actual_amount,
        SUM(ue.actual_amount) - SUM(ue.budget_amount) as variance
    FROM user_expenses ue
    JOIN users u ON ue.user_id = u.id
    JOIN expenses e ON ue.expenses_id = e.id
    WHERE u.username = ? AND ue.year = 2025
    GROUP BY ue.month, e.category
    ORDER BY ue.month, e.category
    """
    
    try:
        df = con.execute(query, [username]).fetchdf()
        con.close()
        
        if df.empty:
            return "<div><p>No variance data available.</p></div>"
        
        fig = go.Figure()
        
        categories = df['category'].unique()
        
        for category in categories:
            category_df = df[df['category'] == category]
            
            # Color code: red for over budget, green for under budget
            colors = ['red' if var > 0 else 'green' for var in category_df['variance']]
            
            fig.add_trace(go.Bar(
                x=[f"{month}" for month in category_df['month']],
                y=category_df['variance'],
                name=f'{category.title()}',
                marker_color=colors
            ))
        
        fig.update_layout(
            title={
                'text': '🔴 Red = Over Budget | 🟢 Green = Under Budget',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 12}
            },
            xaxis_title='Month',
            yaxis_title='Variance (DKK)',
            template='plotly_white',
            height=400
        )
        
        return plot(fig, output_type='div')
        
    except Exception as e:
        con.close()
        return f"<div><p>Error generating variance chart: {str(e)}</p></div>"