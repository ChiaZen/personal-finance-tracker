import duckdb

# Connect to database
con = duckdb.connect("db/finance.duckdb")

print("=== DATABASE INSPECTION ===\n")

# 1. Show all tables
print("TABLES:")
tables = con.execute("SHOW TABLES;").fetchall()
for table in tables:
    print(f"  - {table[0]}")
print()

# 2. Show table schemas
for table in tables:
    table_name = table[0]
    print(f"SCHEMA for {table_name}:")
    schema = con.execute(f"DESCRIBE {table_name};").fetchall()
    for column in schema:
        print(f"  {column[0]} ({column[1]})")
    print()

# 3. Show data counts
print("ROW COUNTS:")
for table in tables:
    table_name = table[0]
    count = con.execute(f"SELECT COUNT(*) FROM {table_name};").fetchone()[0]
    print(f"  {table_name}: {count} rows")
print()


print("=== CHECKING GOAL TARGET ISSUE ===")

# Check Linda's goal progress records
print("\n1. Linda's goal progress records:")
linda_goals = con.execute("""
    SELECT 
        u.username,
        g.type as goal_type,
        gp.goal_target,
        gp.current_amount,
        gp.date
    FROM goal_progress gp
    JOIN users u ON gp.user_id = u.id
    JOIN goal g ON gp.goal_id = g.id
    WHERE u.username = 'linda'
    ORDER BY gp.date
""").fetchall()

for row in linda_goals:
    print(f"  {row[0]} | {row[1]} | Target: {row[2]} | Current: {row[3]} | Date: {row[4]}")

# Check if there are duplicate goal_target entries
print("\n2. Checking for duplicate goal records:")
duplicate_goals = con.execute("""
    SELECT 
        u.username,
        g.type,
        COUNT(*) as record_count,
        COUNT(DISTINCT gp.goal_target) as unique_targets
    FROM goal_progress gp
    JOIN users u ON gp.user_id = u.id
    JOIN goal g ON gp.goal_id = g.id
    GROUP BY u.username, g.type
    HAVING COUNT(*) > 1
    ORDER BY u.username
""").fetchall()

for row in duplicate_goals:
    print(f"  {row[0]} | {row[1]} | Records: {row[2]} | Unique targets: {row[3]}")

# Check the goals table structure
print("\n3. Goals table structure:")
goals = con.execute("SELECT * FROM goal").fetchall()
for row in goals:
    print(f"  Goal ID: {row[0]} | Type: {row[1]}")

con.close()