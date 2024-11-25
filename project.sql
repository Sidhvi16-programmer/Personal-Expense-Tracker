create Database project;
use project;

CREATE TABLE users ( 
user_id INT AUTO_INCREMENT PRIMARY KEY, 
name VARCHAR(100), 
email VARCHAR(100) UNIQUE 
); 

CREATE TABLE expenses ( 
expense_id INT AUTO_INCREMENT PRIMARY KEY, 
user_id INT, 
amount DECIMAL(10, 2), 
category VARCHAR(50), 
date DATE, 
description VARCHAR(255), 
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE 
); 

CREATE TABLE budgets ( 
budget_id INT AUTO_INCREMENT PRIMARY KEY, 
user_id INT, 
budget_amount DECIMAL(10, 2), 
period VARCHAR(20),  -- 'weekly' or 'monthly' 
start_date DATE, studentinvoicecustomer_2
end_date DATE, 
FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE 
); 
INSERT INTO users (user_id, name, email) VALUES 
(1, 'Alice Smith', 'alice@example.com'), 
(2, 'Bob Johnson', 'bob@example.com'), 
(3, 'Carol Williams', 'carol@example.com');

INSERT INTO expenses (expense_id, user_id, date, amount, category, description) VALUES 
(1, 1, '2024-10-31', 32.97, 'Entertainment', 'Sample expense data'), 
(2, 2, '2024-10-24', 121.75, 'Dining Out', 'Sample expense data'), 
(3, 2, '2024-10-25', 50.67, 'Entertainment', 'Sample expense data'), 
(4, 1, '2024-11-08', 61.04, 'Utilities', 'Sample expense data'), 
(5, 3, '2024-11-09', 141.26, 'Dining Out', 'Sample expense data');

INSERT INTO budgets (budget_id, user_id, budget_amount, period, start_date, end_date) 
VALUES 
(1, 1, 794.45, 'weekly', '2024-10-13', '2024-11-12'), 
(2, 3, 425.87, 'weekly', '2024-10-13', '2024-11-12'), 
(3, 2, 890.11, 'monthly', '2024-10-13', '2024-11-12'), 
(4, 3, 339.07, 'monthly', '2024-10-13', '2024-11-12'), 
(5, 3, 224.22, 'weekly', '2024-10-13','2024-11-12');


use project;
ALTER TABLE users ADD COLUMN role ENUM('admin', 'user') DEFAULT'user';
ALTER TABLE users DROP COLUMN name;
Alter table users add password varchar(255);