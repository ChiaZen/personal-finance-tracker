from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import Transaction
from django.db.models import Sum
from core.charts.income_expenses import generate_monthly_income_vs_expense
from core.charts.expenses_breakdown_category import generate_detailed_breakdown_table, generate_sunburst_chart
from core.charts.budget_vs_actual_expenses import generate_budget_vs_actual_chart,generate_monthly_variance_chart

USER_MAPPING = {
    'TestLydiaOrchard': 'alice',  # Map your user to alice's demo data
}

@login_required
def dashboard_view(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user).order_by('-date')[:10]

    totals = Transaction.objects.filter(user=user).values('type').annotate(total=Sum('amount'))
    summary = {'income': 0, 'expense': 0, 'saving': 0, 'investment': 0}
    for item in totals:
        summary[item['type']] = item['total']
        
    # Get data from your DuckDB database
    import duckdb
    import pandas as pd
    
    con = duckdb.connect("db/finance.duckdb")
    
    # Calculate summary for Lydia, month 1, year 2025
    summary_query = """
    WITH lydia_income AS (
        SELECT 
            SUM(income_after_tax + additional_income) as total_income
        FROM income i
        JOIN users u ON i.user_id = u.id
        WHERE u.username = 'lydia' AND i.month = 1 AND i.year = 2025
    ),
    lydia_expenses AS (
        SELECT 
            SUM(actual_amount) as total_expenses
        FROM user_expenses ue
        JOIN users u ON ue.user_id = u.id
        WHERE u.username = 'lydia' AND ue.month = 1 AND ue.year = 2025
    )
    SELECT 
        COALESCE(li.total_income, 0) as income,
        COALESCE(le.total_expenses, 0) as expense,
        COALESCE(li.total_income, 0) - COALESCE(le.total_expenses, 0) as saving
    FROM lydia_income li
    CROSS JOIN lydia_expenses le
    """
    
    summary_data = con.execute(summary_query).fetchone()
    
    # Create summary dictionary
    summary = {
        'income': summary_data[0] if summary_data else 0,
        'expense': summary_data[1] if summary_data else 0, 
        'saving': summary_data[2] if summary_data else 0,
        'investment': 0  # Not available in current data
    }
    
    # Get user data for charts
    user_data = con.execute("""
        SELECT 
            u.username as user,
            i.date,
            i.income_after_tax,
            i.additional_income,
            COALESCE(exp.budget_expenses, 0) as budget_expenses,
            COALESCE(exp.actual_expenses, 0) as actual_expenses,
            g.type as goal_type,
            gp.goal_target,
            gp.current_amount as goal_current_amount,
            h.type as household_type
        FROM users u
        LEFT JOIN income i ON u.id = i.user_id
        LEFT JOIN household h ON i.household_id = h.id
        LEFT JOIN (
            SELECT 
                user_id,
                date,
                SUM(budget_amount) as budget_expenses,
                SUM(actual_amount) as actual_expenses
            FROM user_expenses
            GROUP BY user_id, date
        ) exp ON u.id = exp.user_id AND i.date = exp.date
        LEFT JOIN goal_progress gp ON u.id = gp.user_id AND i.date = gp.date
        LEFT JOIN goal g ON gp.goal_id = g.id
        WHERE u.username = 'lydia' AND i.month = 1 AND i.year = 2025
        ORDER BY i.date
    """).fetchdf()
    
    con.close()

    chart_html = generate_monthly_income_vs_expense(user)
    #radar_plot_html = generate_radar_chart(user)
    budget_vs_actual_html = generate_budget_vs_actual_chart('lydia')
    sunburst_html = generate_sunburst_chart('lydia')
    breakdown_table = generate_detailed_breakdown_table('lydia')
    variance_chart = generate_monthly_variance_chart('lydia')

    return render(request, 'dashboard.html', {
        'transactions': transactions,
        'summary': summary,
        'chart_html': chart_html,
        'radar_plot_html': sunburst_html,
        'breakdown_table': breakdown_table,
        'budget_vs_actual_html': budget_vs_actual_html,
        'variance_chart': variance_chart,
    })

def summarize_transactions(user):
    txs = Transaction.objects.filter(user=user)
    
    summary = {
        'income': 0,
        'expense': 0,
        'saving': 0,
        'investment': 0,
        'debt': 0,
        'loan': 0,
    }

    for tx in txs:
        summary[tx.type] += tx.amount

    return summary