import sqlite3

# create database
conn = sqlite3.connect('admin.db')

cursor = conn.cursor()

# create admin table
cursor.execute("""
CREATE TABLE IF NOT EXISTS admin (
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT
)
""")

# insert default admin
cursor.execute("""
INSERT INTO admin (username,password)
VALUES ('admin','admin123')
""")

conn.commit()
conn.close()

print("Admin database created successfully!")