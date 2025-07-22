import duckdb
import os

os.makedirs('db', exist_ok=True)

csv1_path = 'core/data/mock_finance_data.csv'
csv2_path = 'core/data/detailed_budget_expenses.csv'

con = duckdb.connect("db/finance.duckdb")

con.execute(f"""
    CREATE TABLE IF NOT EXISTS user_summary AS 
    SELECT * FROM read_csv_auto('{csv1_path}', HEADER=TRUE);
""")

con.execute(f"""
    CREATE TABLE IF NOT EXISTS monthly_budget AS 
    SELECT * FROM read_csv_auto('{csv2_path}', HEADER=TRUE);
""")

# Step 1: Create users table
con.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER,
    username TEXT,
    household_type TEXT
);
""")

# Step 2: Create user_summary table
con.execute("""
CREATE TABLE IF NOT EXISTS user_summary (
    summary_id INTEGER,
    user_id INTEGER,
    date DATE,
    goal_type TEXT,
    goal_target DOUBLE,
    goal_current_amount DOUBLE,
    income_after_tax DOUBLE,
    budget_expenses DOUBLE,
    actual_expenses DOUBLE
);
""")

# Step 3: Create monthly_budget table
con.execute("""
CREATE TABLE IF NOT EXISTS monthly_budget (
    budget_id INTEGER,
    user_id INTEGER,
    date DATE,
    category TEXT,
    budget_amount DOUBLE
);
""")

# Step 4: Populate users table with data from user_summary
# Extract unique users and assign IDs
con.execute("""
INSERT INTO users (user_id, username, household_type)
SELECT 
    ROW_NUMBER() OVER (ORDER BY user) as user_id,
    user as username,
    household_type
FROM (
    SELECT DISTINCT user, household_type 
    FROM user_summary
) unique_users;
""")


con.close()