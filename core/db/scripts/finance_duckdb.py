import duckdb
import os

def setup_database():
    # Clean start - remove existing database
    if os.path.exists("db/finance.duckdb"):
        os.remove("db/finance.duckdb")
        print("🗑️ Removed existing database")

    os.makedirs('db', exist_ok=True)

    # CSV file paths
    data_path = 'core/db/data/'
    expenses_csv = os.path.join(data_path, 'mock_expenses.csv')
    income_csv = os.path.join(data_path, 'mock_additional_income.csv')
    goals_csv = os.path.join(data_path, 'mock_goals_income.csv')

    con = duckdb.connect("db/finance.duckdb")

    print("Creating database schema...")

    # 1. CREATE TABLES WITH DATE, MONTH, YEAR COLUMNS
    
    # Users table
    con.execute("""
        CREATE SEQUENCE user_seq START 1;
        CREATE TABLE users (
            id INTEGER PRIMARY KEY DEFAULT nextval('user_seq'),
            username VARCHAR UNIQUE NOT NULL
        );
    """)

    # Household lookup table
    con.execute("""
        CREATE SEQUENCE household_seq START 1;
        CREATE TABLE household (
            id INTEGER PRIMARY KEY DEFAULT nextval('household_seq'),
            type VARCHAR UNIQUE
        );
    """)

    # Goal types lookup table
    con.execute("""
        CREATE SEQUENCE goal_seq START 1;
        CREATE TABLE goal (
            id INTEGER PRIMARY KEY DEFAULT nextval('goal_seq'),
            type VARCHAR UNIQUE
        );
    """)

    # Expenses categories lookup table
    con.execute("""
        CREATE SEQUENCE expenses_seq START 1;
        CREATE TABLE expenses (
            id INTEGER PRIMARY KEY DEFAULT nextval('expenses_seq'),
            category VARCHAR UNIQUE
        );
    """)

    # Income table - WITH DATE, MONTH, YEAR
    con.execute("""
        CREATE SEQUENCE income_seq START 1;
        CREATE TABLE income (
            id INTEGER PRIMARY KEY DEFAULT nextval('income_seq'),
            user_id INTEGER NOT NULL,
            date DATE NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            income_after_tax DECIMAL(10,2) NOT NULL,
            additional_income DECIMAL(10,2) DEFAULT 0,
            household_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (household_id) REFERENCES household(id)
        );
    """)

    # User expenses table - WITH DATE, MONTH, YEAR
    con.execute("""
        CREATE SEQUENCE user_expenses_seq START 1;
        CREATE TABLE user_expenses (
            id INTEGER PRIMARY KEY DEFAULT nextval('user_expenses_seq'),
            user_id INTEGER NOT NULL,
            expenses_id INTEGER NOT NULL,
            date DATE NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            budget_amount DECIMAL(10,2) NOT NULL,
            actual_amount DECIMAL(10,2),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (expenses_id) REFERENCES expenses(id)
        );
    """)

    # Goal progress table - WITH DATE, MONTH, YEAR
    con.execute("""
        CREATE SEQUENCE goal_progress_seq START 1;
        CREATE TABLE goal_progress (
            id INTEGER PRIMARY KEY DEFAULT nextval('goal_progress_seq'),
            user_id INTEGER NOT NULL,
            goal_id INTEGER NOT NULL,
            goal_target DECIMAL(12,2) NOT NULL,
            current_amount DECIMAL(12,2) NOT NULL,
            date DATE NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (goal_id) REFERENCES goal(id)
        );
    """)

    print("✅ Database schema created!")

    # 2. POPULATE LOOKUP TABLES

    # Check and load goals CSV to extract data
    if os.path.exists(goals_csv):
        # Extract unique household types
        households = con.execute(f"""
            SELECT DISTINCT household_type 
            FROM read_csv_auto('{goals_csv}', HEADER=TRUE)
        """).fetchall()
        
        for household_type, in households:
            con.execute("INSERT INTO household (type) VALUES (?)", [household_type])
        
        # Extract unique goal types
        goal_types = con.execute(f"""
            SELECT DISTINCT goal_type 
            FROM read_csv_auto('{goals_csv}', HEADER=TRUE)
        """).fetchall()
        
        for goal_type, in goal_types:
            con.execute("INSERT INTO goal (type) VALUES (?)", [goal_type])
        
        print("✅ Household and goal types populated")

    # Extract expense categories from expenses CSV
    if os.path.exists(expenses_csv):
        expense_categories = con.execute(f"""
            SELECT DISTINCT expenses_category 
            FROM read_csv_auto('{expenses_csv}', HEADER=TRUE)
        """).fetchall()
        
        for category, in expense_categories:
            con.execute("INSERT INTO expenses (category) VALUES (?)", [category])
        
        print("✅ Expense categories populated")

    # 3. POPULATE MAIN TABLES

    # Populate users from goals CSV
    if os.path.exists(goals_csv):
        users = con.execute(f"""
            SELECT DISTINCT user 
            FROM read_csv_auto('{goals_csv}', HEADER=TRUE)
        """).fetchall()
        
        for username, in users:
            con.execute("INSERT INTO users (username) VALUES (?)", [username])
        
        print("✅ Users populated")

        # FIXED: Populate income table - Force date column as VARCHAR first
        con.execute(f"""
            INSERT INTO income (user_id, date, month, year, income_after_tax, household_id)
            SELECT 
                u.id as user_id,
                strptime(CAST(g.date AS VARCHAR), '%d/%m/%Y')::DATE as date,
                EXTRACT(month FROM strptime(CAST(g.date AS VARCHAR), '%d/%m/%Y')::DATE) as month,
                EXTRACT(year FROM strptime(CAST(g.date AS VARCHAR), '%d/%m/%Y')::DATE) as year,
                g.income_after_tax,
                h.id as household_id
            FROM read_csv_auto('{goals_csv}', HEADER=TRUE, types={{'date': 'VARCHAR'}}) g
            JOIN users u ON u.username = g.user
            JOIN household h ON h.type = g.household_type
        """)
        print("✅ Income data loaded with date/month/year")

        # FIXED: Populate goal progress
        con.execute(f"""
            INSERT INTO goal_progress (user_id, goal_id, goal_target, current_amount, date, month, year)
            SELECT 
                u.id as user_id,
                gl.id as goal_id,
                g.goal_target,
                g.goal_current_amount,
                strptime(CAST(g.date AS VARCHAR), '%d/%m/%Y')::DATE as date,
                EXTRACT(month FROM strptime(CAST(g.date AS VARCHAR), '%d/%m/%Y')::DATE) as month,
                EXTRACT(year FROM strptime(CAST(g.date AS VARCHAR), '%d/%m/%Y')::DATE) as year
            FROM read_csv_auto('{goals_csv}', HEADER=TRUE, types={{'date': 'VARCHAR'}}) g
            JOIN users u ON u.username = g.user
            JOIN goal gl ON gl.type = g.goal_type
        """)
        print("✅ Goal progress loaded with date/month/year")

    # FIXED: Load additional income 
    if os.path.exists(income_csv):
        # First, create users from additional income CSV that don't exist
        con.execute(f"""
            INSERT INTO users (username)
            SELECT DISTINCT ai.user
            FROM read_csv_auto('{income_csv}', HEADER=TRUE, types={{'date': 'VARCHAR'}}) ai
            WHERE ai.user NOT IN (SELECT username FROM users)
        """)
        
        # Create income records for additional income users
        con.execute(f"""
            INSERT INTO income (user_id, date, month, year, income_after_tax, additional_income)
            SELECT 
                u.id as user_id,
                strptime(ai.date, '%d/%m/%Y')::DATE as date,
                EXTRACT(month FROM strptime(ai.date, '%d/%m/%Y')::DATE) as month,
                EXTRACT(year FROM strptime(ai.date, '%d/%m/%Y')::DATE) as year,
                0 as income_after_tax,
                ai.additional_income
            FROM read_csv_auto('{income_csv}', HEADER=TRUE, types={{'date': 'VARCHAR'}}) ai
            JOIN users u ON u.username = ai.user
            WHERE NOT EXISTS (
                SELECT 1 FROM income i 
                WHERE i.user_id = u.id 
                AND i.date = strptime(ai.date, '%d/%m/%Y')::DATE
            )
        """)
        
        # Update existing records with additional income
        con.execute(f"""
            UPDATE income 
            SET additional_income = ai.additional_income
            FROM (
                SELECT 
                    u.id as user_id, 
                    strptime(ai.date, '%d/%m/%Y')::DATE as date,
                    ai.additional_income
                FROM read_csv_auto('{income_csv}', HEADER=TRUE, types={{'date': 'VARCHAR'}}) ai
                JOIN users u ON u.username = ai.user
            ) ai
            WHERE income.user_id = ai.user_id 
            AND income.date = ai.date
        """)
        print("✅ Additional income updated with date/month/year")

    # FIXED: Load expenses
    if os.path.exists(expenses_csv):
        con.execute(f"""
            INSERT INTO user_expenses (user_id, expenses_id, date, month, year, budget_amount, actual_amount)
            SELECT 
                u.id as user_id,
                e.id as expenses_id,
                strptime(ex.date, '%d/%m/%Y')::DATE as date,
                EXTRACT(month FROM strptime(ex.date, '%d/%m/%Y')::DATE) as month,
                EXTRACT(year FROM strptime(ex.date, '%d/%m/%Y')::DATE) as year,
                ex.budget_amount,
                ex.actual_amount_spent
            FROM read_csv_auto('{expenses_csv}', HEADER=TRUE, types={{'date': 'VARCHAR'}}) ex
            JOIN users u ON u.username = ex.user
            JOIN expenses e ON e.category = ex.expenses_category
        """)
        print("✅ Expenses data loaded with date/month/year")

    # 4. VERIFICATION
    print("\n=== DATABASE VERIFICATION ===")

    tables = ['users', 'household', 'goal', 'expenses', 'income', 'user_expenses', 'goal_progress']
    for table in tables:
        count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table}: {count} rows")

    # 5. SAMPLE QUERIES WITH DATE/MONTH/YEAR
    print("\n=== SAMPLE QUERIES ===")

    print("\nMonthly income summary:")
    monthly_income = con.execute("""
        SELECT 
            u.username,
            i.month,
            i.year,
            SUM(i.income_after_tax) as total_income_after_tax,
            SUM(i.additional_income) as total_additional_income
        FROM income i
        JOIN users u ON u.id = i.user_id
        WHERE i.year = 2025 AND i.month = 1
        GROUP BY u.username, i.month, i.year
        ORDER BY u.username
        LIMIT 5
    """).fetchall()
    for row in monthly_income:
        print(f"  {row[0]} ({row[1]}/{row[2]}): Income: {row[3]}, Additional: {row[4]}")

    print("\nExpenses by month:")
    monthly_expenses = con.execute("""
        SELECT 
            ue.month,
            ue.year,
            COUNT(*) as transactions,
            SUM(ue.budget_amount) as total_budget,
            SUM(ue.actual_amount) as total_actual
        FROM user_expenses ue
        WHERE ue.year = 2025
        GROUP BY ue.month, ue.year
        ORDER BY ue.month
    """).fetchall()
    for row in monthly_expenses:
        print(f"  {row[0]}/{row[1]}: {row[2]} transactions, Budget: {row[3]}, Actual: {row[4]}")

    con.close()
    print("\n✅ Database setup completed successfully!")

if __name__ == "__main__":
    setup_database()