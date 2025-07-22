CREATE TABLE user_expenses (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  expenses_id INTEGER NOT NULL,
  date DATE UNIQUE NOT NULL,
  month INTEGER NOT NULL,
  year INTEGER NOT NULL,
  budget_amount DECIMAL(10,2) NOT NULL,
  actual_amount DECIMAL(10,2),
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (expenses_id) REFERENCES expenses(id)
);  