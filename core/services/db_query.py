import duckdb
import pandas as pd
from pathlib import Path


def fetch_user_summary():
    con = duckdb.connect("db/finance.duckdb")
    query = """
    SELECT 
        u.username as user,
        i.date,
        i.income_after_tax,
        -- Calculate budget and actual expenses per user per date
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
    WHERE i.date IS NOT NULL
    ORDER BY u.username, i.date
    """
    df = con.execute(query).fetchdf()
    con.close()

    # Ensure date column is datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    return df


def fetch_monthly_expenses_by_user(username=None):
    """Fetch monthly expenses breakdown by category for a specific user or all users"""
    con = duckdb.connect("db/finance.duckdb")

    where_clause = ""
    if username:
        where_clause = f"WHERE u.username = '{username}'"

    query = f"""
    SELECT 
        u.username as user,
        ue.year,
        ue.month,
        e.category as expenses_category,
        SUM(ue.budget_amount) as budget_amount,
        SUM(ue.actual_amount) as actual_amount_spent
    FROM user_expenses ue
    JOIN users u ON ue.user_id = u.id
    JOIN expenses e ON ue.expenses_id = e.id
    {where_clause}
    GROUP BY u.username, ue.year, ue.month, e.category
    ORDER BY u.username, ue.year, ue.month, e.category
    """

    df = con.execute(query).fetchdf()
    con.close()
    return df


def fetch_monthly_income_by_user(username=None):
    """Fetch monthly income data for a specific user or all users"""
    con = duckdb.connect("db/finance.duckdb")

    where_clause = ""
    if username:
        where_clause = f"WHERE u.username = '{username}'"

    query = f"""
    SELECT 
        u.username as user,
        i.year,
        i.month,
        i.date,
        i.income_after_tax,
        i.additional_income,
        h.type as household_type
    FROM income i
    JOIN users u ON i.user_id = u.id
    LEFT JOIN household h ON i.household_id = h.id
    {where_clause}
    ORDER BY u.username, i.year, i.month, i.date
    """

    df = con.execute(query).fetchdf()
    con.close()

    # Ensure date column is datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    return df


def fetch_goal_progress_by_user(username=None):
    """Fetch goal progress data for a specific user or all users"""
    con = duckdb.connect("db/finance.duckdb")

    where_clause = ""
    if username:
        where_clause = f"WHERE u.username = '{username}'"

    query = f"""
    SELECT 
        u.username as user,
        g.type as goal_type,
        gp.goal_target,
        gp.current_amount as goal_current_amount,
        gp.date,
        gp.year,
        gp.month
    FROM goal_progress gp
    JOIN users u ON gp.user_id = u.id
    JOIN goal g ON gp.goal_id = g.id
    {where_clause}
    ORDER BY u.username, gp.date
    """

    df = con.execute(query).fetchdf()
    con.close()

    # Ensure date column is datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    return df


def fetch_user_data_for_dashboard(username):
    """Fetch comprehensive user data for dashboard charts"""
    con = duckdb.connect("db/finance.duckdb")

    query = """
    SELECT 
        u.username as user,
        i.date,
        i.year,
        i.month,
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
    WHERE u.username = ? AND i.date IS NOT NULL
    ORDER BY i.date
    """

    df = con.execute(query, [username]).fetchdf()
    con.close()

    # Ensure date column is datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    return df


def fetch_all_users():
    """Fetch all users in the database"""
    con = duckdb.connect("db/finance.duckdb")
    query = "SELECT username FROM users ORDER BY username"
    df = con.execute(query).fetchdf()
    con.close()
    return df['username'].tolist()


def fetch_expense_categories():
    """Fetch all expense categories"""
    con = duckdb.connect("db/finance.duckdb")
    query = "SELECT category FROM expenses ORDER BY category"
    df = con.execute(query).fetchdf()
    con.close()
    return df['category'].tolist()
