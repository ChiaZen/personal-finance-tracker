import plotly.graph_objs as go
from plotly.offline import plot
import duckdb
import pandas as pd

def generate_sunburst_chart(username):
    """Generate a sunburst chart showing expense categories as % of total income"""
    con = duckdb.connect("db/finance.duckdb")
    
    # Get user's total income and expenses by category
    query = """
    WITH user_totals AS (
        SELECT 
            u.username,
            SUM(i.income_after_tax + i.additional_income) as total_income,
            SUM(ue.actual_amount) as total_expenses
        FROM users u
        LEFT JOIN income i ON u.id = i.user_id
        LEFT JOIN user_expenses ue ON u.id = ue.user_id
        WHERE u.username = ?
        GROUP BY u.username
    ),
    category_expenses AS (
        SELECT 
            u.username,
            e.category,
            SUM(ue.actual_amount) as category_spent,
            ut.total_income,
            ut.total_expenses
        FROM users u
        JOIN user_expenses ue ON u.id = ue.user_id
        JOIN expenses e ON ue.expenses_id = e.id
        CROSS JOIN user_totals ut
        WHERE u.username = ? AND ut.username = u.username
        GROUP BY u.username, e.category, ut.total_income, ut.total_expenses
    )
    SELECT 
        category,
        category_spent,
        total_income,
        total_expenses,
        ROUND((category_spent / total_income) * 100, 1) as pct_of_income,
        ROUND((category_spent / total_expenses) * 100, 1) as pct_of_total_expenses
    FROM category_expenses
    ORDER BY category_spent DESC
    """
    
    try:
        df = con.execute(query, [username, username]).fetchdf()
        con.close()
        
        if df.empty:
            return "<div><p>No expense data available for sunburst chart.</p></div>"
            
        # Calculate remaining income (savings/unspent)
        total_income = df['total_income'].iloc[0]
        total_expenses = df['total_expenses'].iloc[0]
        remaining_income = total_income - total_expenses
        remaining_pct = (remaining_income / total_income) * 100
        
        # Prepare data for sunburst
        labels = ['Total Income']  # Root
        parents = ['']  # Root has no parent
        values = [total_income]
        colors = ['#1f77b4']  # Root color
        
        # Add main categories: Expenses and Savings
        labels.extend(['Expenses', 'Savings/Unspent'])
        parents.extend(['Total Income', 'Total Income'])
        values.extend([total_expenses, remaining_income])
        colors.extend(['#d62728', '#2ca02c'])  # Red for expenses, green for savings
        
        # Add expense categories under "Expenses"
        category_colors = ['#ff7f0e', '#ffbb78', '#c49c94', '#f7b6d3', '#c7c7c7', '#dbdb8d', '#17becf']
        for i, row in df.iterrows():
            labels.append(f"{row['category'].title()}")
            parents.append('Expenses')
            values.append(row['category_spent'])
            colors.append(category_colors[i % len(category_colors)])
        
        # Create sunburst chart
        fig = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(colors=colors),
            hovertemplate='<b>%{label}</b><br>' +
                         'Amount: %{value:,.0f} DKK<br>' +
                         'Percentage: %{percentParent}<br>' +
                         '<extra></extra>',
            maxdepth=3,
        ))
        
        fig.update_layout(
            title={
                'text': f"💰 Income vs Expenses Breakdown - {username.title()}",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },
            font=dict(size=12),
            height=500,
            margin=dict(t=60, b=20, l=20, r=20),
            annotations=[
                dict(
                    text=f"<b>Total Income:</b> {total_income:,.0f} DKK<br>" +
                         f"<b>Total Expenses:</b> {total_expenses:,.0f} DKK<br>" +
                         f"<b>Savings Rate:</b> {remaining_pct:.1f}%",
                    showarrow=False,
                    x=0.5, y=-0.1,
                    xref="paper", yref="paper",
                    xanchor="center",
                    font=dict(size=10)
                )
            ]
        )
        
        return plot(fig, output_type='div')
        
    except Exception as e:
        con.close()
        return f"<div><p>Error generating sunburst chart: {str(e)}</p></div>"

def generate_detailed_breakdown_table(username):
    """Generate a detailed table showing expense breakdown with percentages"""
    con = duckdb.connect("db/finance.duckdb")
    
    query = """
    WITH user_totals AS (
        SELECT 
            u.username,
            SUM(i.income_after_tax + i.additional_income) as total_income
        FROM users u
        LEFT JOIN income i ON u.id = i.user_id
        WHERE u.username = ?
        GROUP BY u.username
    )
    SELECT 
        e.category,
        SUM(ue.budget_amount) as budgeted,
        SUM(ue.actual_amount) as actual_spent,
        SUM(ue.actual_amount) - SUM(ue.budget_amount) as variance,
        ut.total_income,
        ROUND((SUM(ue.actual_amount) / ut.total_income) * 100, 1) as pct_of_income,
        ROUND((SUM(ue.budget_amount) / ut.total_income) * 100, 1) as budget_pct_of_income
    FROM users u
    JOIN user_expenses ue ON u.id = ue.user_id
    JOIN expenses e ON ue.expenses_id = e.id
    CROSS JOIN user_totals ut
    WHERE u.username = ? AND ut.username = u.username
    GROUP BY e.category, ut.total_income
    ORDER BY actual_spent DESC
    """
    
    try:
        df = con.execute(query, [username, username]).fetchdf()
        con.close()
        
        if df.empty:
            return "<div><p>No data available for breakdown table.</p></div>"
        
        # Create HTML table
        html = f"""
        <div style="margin-top: 20px;">
            <h4>📊 Detailed Expense Breakdown - {username.title()}</h4>
            <table class="table table-striped" style="font-size: 14px;">
                <thead>
                    <tr>
                        <th>Category</th>
                        <th>Budgeted</th>
                        <th>Actual</th>
                        <th>Variance</th>
                        <th>% of Income</th>
                        <th>Budget % of Income</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for _, row in df.iterrows():
            variance_color = "text-success" if row['variance'] <= 0 else "text-danger"
            html += f"""
                    <tr>
                        <td><strong>{row['category'].title()}</strong></td>
                        <td>{row['budgeted']:,.0f} DKK</td>
                        <td>{row['actual_spent']:,.0f} DKK</td>
                        <td class="{variance_color}">{row['variance']:+,.0f} DKK</td>
                        <td><span class="badge bg-primary">{row['pct_of_income']:.1f}%</span></td>
                        <td><span class="badge bg-secondary">{row['budget_pct_of_income']:.1f}%</span></td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        
        return html
        
    except Exception as e:
        con.close()
        return f"<div><p>Error generating breakdown table: {str(e)}</p></div>"
