TABLE income (
  id INTEGER PRIMARY KEY
  user_id INTEGER NOT NULL
  household_id integer
  income_after_tax decimal(10,2) NOT NULL
  additional_income decimal(10,2) DEFAULT 0
  month integer NOT NULL
  year integer NOT NULL
  date DATE
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (household_id) REFERENCES household(id)   
);