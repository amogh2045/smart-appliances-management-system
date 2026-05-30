import sqlite3

con = sqlite3.connect("products.db")
cur = con.cursor()

cur.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    address TEXT,
    phone TEXT
)
""")

cur.execute("""
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    price INTEGER,
    shop TEXT
)
""")

products = [
("Smart Fan","Cooling",2000,"Taranga Electronics - Sirsi"),
("Smart AC","Cooling",35000,"Taranga Electronics - Sirsi"),
("Smart Washing Machine","Laundry",25000,"Taranga Electronics - Sirsi"),
("Smart Refrigerator","Kitchen",30000,"Taranga Electronics - Sirsi"),
("Smart Television","Entertainment",40000,"Taranga Electronics - Sirsi")
]

cur.executemany(
"INSERT INTO products(name,category,price,shop) VALUES(?,?,?,?)",
products
)

con.commit()
con.close()

print("Database created successfully")