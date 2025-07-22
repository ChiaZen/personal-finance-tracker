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

# 4. Show sample data from user_summary
print("SAMPLE DATA from user_summary:")
try:
    sample_data = con.execute("SELECT * FROM user_summary LIMIT 3;").fetchall()
    columns = [desc[0] for desc in con.description]
    print(f"  Columns: {columns}")
    for row in sample_data:
        print(f"  {row}")
except Exception as e:
    print(f"  Error: {e}")
    
print("=== DATABASE STATUS ===")

# Check tables
tables = con.execute("SHOW TABLES").fetchall()
print(f"Tables: {[t[0] for t in tables]}")

# Check user_summary data
if ('user_summary',) in tables:
    count = con.execute("SELECT COUNT(*) FROM user_summary").fetchone()[0]
    users = con.execute("SELECT DISTINCT user FROM user_summary").fetchall()
    print(f"user_summary rows: {count}")
    print(f"Users in database: {[u[0] for u in users]}")
    
    # Show sample data
    sample = con.execute("SELECT * FROM user_summary LIMIT 3").fetchall()
    print("Sample data:")
    for row in sample:
        print(f"  {row}")
else:
    print("❌ user_summary table not found!")


con.close()