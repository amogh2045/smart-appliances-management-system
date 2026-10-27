import sqlite3
import random
import os
import re
import string
from flask import Flask, render_template, request, redirect, session
from werkzeug.utils import secure_filename

#-----------EMAIL-----OTP---SENDER----------
import smtplib
from email.mime.text import MIMEText

def send_email_otp(to_email, otp):

    sender_email = "smartappliances196@gmail.com"
    sender_password = "glft kais xkrj pdnf"   # 🔥 paste here

    subject = "Your OTP Code"
    body = f"Your OTP is: {otp}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print("OTP sent to email ✅")
    except Exception as e:
        print("Email Error:", e)


app = Flask(__name__)
app.secret_key = "super_secure_random_key_123!@#"

UPLOAD_FOLDER = 'static/products'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- HELPER ----------------
def notify(msg):
    session["notification"] = msg


def get_cart_total_items():
    cart = session.get("cart", {})
    return sum(int(quantity) for quantity in cart.values())


def generate_captcha(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# ---------------- DATABASE INIT ----------------
def init_db():

    con = sqlite3.connect("products.db")
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        brand TEXT,
        capacity TEXT,
        type TEXT,
        energy TEXT,
        price INTEGER CHECK(price >= 0),
        seller TEXT,
        image TEXT,
        stock INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS product_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        product_id INTEGER,
        message TEXT,
        status TEXT DEFAULT 'Pending'
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        rating INTEGER,
        comment TEXT,
        product_id INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        product_id INTEGER
    )
    """)

    con.commit()
    con.close()

    con = sqlite3.connect("users.db")
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        address TEXT,
        phone TEXT,
        email TEXT UNIQUE
    )
    """)

    con.commit()
    con.close()

init_db()

# ---------------- HOME ----------------
@app.route("/")
def home():

    category = request.args.get("category")

    con = sqlite3.connect("products.db")
    cur = con.cursor()

    if category:
        cur.execute("SELECT * FROM products WHERE category=?", (category,))
    else:
        cur.execute("SELECT * FROM products")

    products = cur.fetchall()
    con.close()

    return render_template("index.html", products=products, selected_category=category)

# ---------------- PRODUCT DETAIL ----------------
@app.route("/product/<int:pid>")
def product_detail(pid):

    con = sqlite3.connect("products.db")
    cur = con.cursor()

    cur.execute("SELECT * FROM products WHERE id=?", (pid,))
    product = cur.fetchone()

    cur.execute("SELECT * FROM reviews WHERE product_id=?", (pid,))
    reviews = cur.fetchall()

    availability = None
    request_status = None

    if "user" in session:

        # ✅ FIX: avoid duplicate history
        cur.execute("""
        SELECT * FROM user_history
        WHERE username=? AND product_id=?
        """, (session["user"], pid))

        if not cur.fetchone():
            cur.execute("INSERT INTO user_history (username, product_id) VALUES (?,?)",
                        (session["user"], pid))

        cur.execute("""
        SELECT status FROM product_requests
        WHERE username=? AND product_id=?
        """, (session["user"], pid))

        req = cur.fetchone()
        if req:
            request_status = req[0]

        con2 = sqlite3.connect("users.db")
        cur2 = con2.cursor()

        cur2.execute("SELECT address FROM users WHERE username=?", (session["user"],))
        data = cur2.fetchone()
        con2.close()

        if data:
            if "sirsi" in data[0].lower():
                availability = "Available ✅"
            else:
                availability = "Not Available ❌"

    con.commit()
    con.close()

    return render_template("product_detail.html",
                           product=product,
                           reviews=reviews,
                           availability=availability,
                           request_status=request_status)

# ---------------- ADD PRODUCT ----------------
@app.route('/add_product', methods=['POST'])
def add_product():

    if "admin" not in session:
        return redirect("/admin")

    name = request.form.get("name")
    category = request.form.get("category")
    brand = request.form.get("brand")
    capacity = request.form.get("capacity")
    type_ = request.form.get("type")
    energy = request.form.get("energy")
    price = request.form.get("price")
    seller = request.form.get("seller")
    stock = request.form.get("stock")

    if not all([name, category, brand, capacity, type_, price, seller, stock]):
        notify("All fields required ⚠️")
        return redirect("/admin_dashboard")

    try:
        price = int(price)
        stock = int(stock)
        if price <= 0 or stock < 0:
            raise ValueError
    except:
        notify("Invalid price/stock ❌")
        return redirect("/admin_dashboard")

    image = request.files.get("image")
    filename = None

    if image and image.filename != "":
        filename = secure_filename(image.filename)
        image.save(os.path.join(UPLOAD_FOLDER, filename))

    con = sqlite3.connect("products.db")
    cur = con.cursor()

    cur.execute("""
    INSERT INTO products 
    (name, category, brand, capacity, type, energy, price, seller, image, stock)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name, category, brand, capacity, type_,
        energy, price, seller, filename, stock
    ))

    con.commit()
    con.close()

    notify("Product Added ✅")
    return redirect("/admin_dashboard")

# ---------------- DELETE PRODUCT ----------------
@app.route('/delete_product/<int:pid>', methods=['GET','POST'])
def delete_product(pid):

    if "admin" not in session:
        return redirect("/admin")

    con = sqlite3.connect("products.db")
    cur = con.cursor()

    cur.execute("DELETE FROM products WHERE id=?", (pid,))

    con.commit()
    con.close()

    notify("Product Deleted ✅")
    return redirect("/admin_dashboard")

# ---------------- ADD TO CART ----------------
@app.route('/add_to_cart/<int:pid>', methods=['GET','POST'])  # ✅ FIX
def add_to_cart(pid):

    con = sqlite3.connect("products.db")
    cur = con.cursor()
    cur.execute("SELECT stock FROM products WHERE id=?", (pid,))
    data = cur.fetchone()
    con.close()

    if not data:
        notify("Product not found ❌")
        return redirect("/")

    stock = data[0]

    if "cart" not in session:
        session["cart"] = {}

    cart = session["cart"]
    pid = str(pid)

    if cart.get(pid, 0) >= stock:
        notify("Stock limit reached ❌")
        return redirect("/")

    cart[pid] = cart.get(pid, 0) + 1
    session.modified = True
    total_items = get_cart_total_items()
    item_word = "product" if total_items == 1 else "products"

    notify(f"{total_items} {item_word} have been added to your cart")
    return redirect("/")

# ---------------- INCREASE ----------------
@app.route('/increase/<int:pid>', methods=['GET','POST'])  # ✅ FIX
def increase(pid):

    con = sqlite3.connect("products.db")
    cur = con.cursor()
    cur.execute("SELECT stock FROM products WHERE id=?", (pid,))
    data = cur.fetchone()
    con.close()

    if not data:
        return redirect("/cart")

    stock = data[0]

    cart = session.get("cart", {})
    pid = str(pid)

    if cart.get(pid, 0) < stock:
        cart[pid] += 1
    else:
        notify("Stock limit reached ⚠️")

    session["cart"] = cart
    return redirect("/cart")

# ---------------- DECREASE ----------------
@app.route('/decrease/<int:pid>', methods=['GET','POST'])  # ✅ FIX
def decrease(pid):

    cart = session.get("cart", {})
    pid = str(pid)

    if pid in cart:
        cart[pid] -= 1
        if cart[pid] <= 0:
            del cart[pid]

    session["cart"] = cart
    return redirect("/cart")

# ---------------- REMOVE ----------------
@app.route('/remove_from_cart/<int:pid>', methods=['GET','POST'])  # ✅ FIX
def remove_from_cart(pid):

    cart = session.get("cart", {})
    pid = str(pid)

    if pid in cart:
        del cart[pid]

    session["cart"] = cart
    return redirect("/cart")

# ---------------- CART PAGE ----------------
@app.route('/cart')
def cart():

    cart = session.get("cart", {})
    if not cart:
        return render_template("cart.html", cart_items=[], total=0)

    ids = list(map(int, cart.keys()))

    con = sqlite3.connect("products.db")
    cur = con.cursor()
    query = "SELECT * FROM products WHERE id IN ({})".format(",".join("?"*len(ids)))
    cur.execute(query, ids)
    products = cur.fetchall()
    con.close()

    cart_items = []
    total = 0

    for p in products:
        qty = cart[str(p[0])]
        subtotal = p[7] * qty
        total += subtotal
        cart_items.append({"product": p, "quantity": qty, "subtotal": subtotal})

    return render_template("cart.html", cart_items=cart_items, total=total)

# ---------------- REQUEST PRODUCT ----------------
@app.route('/request_product/<int:pid>', methods=['POST'])
def request_product(pid):

    if "user" not in session:
        return redirect("/login")

    message = request.form.get("message")

    con = sqlite3.connect("products.db")
    cur = con.cursor()

    cur.execute("""
    SELECT * FROM product_requests
    WHERE username=? AND product_id=?
    """, (session["user"], pid))

    if cur.fetchone():
        notify("Already requested ⚠️")
    else:
        cur.execute("""
        INSERT INTO product_requests (username, product_id, message)
        VALUES (?, ?, ?)
        """, (session["user"], pid, message))
        notify("Request sent 📩")

    con.commit()
    con.close()

    return redirect(f"/product/{pid}")

# ---------------- MY REQUESTS ----------------
@app.route('/my_requests')
def my_requests():

    if "user" not in session:
        return redirect("/login")

    con = sqlite3.connect("products.db")
    cur = con.cursor()

    cur.execute("""
    SELECT r.id, p.name, r.message, r.status
    FROM product_requests r
    JOIN products p ON r.product_id = p.id
    WHERE r.username=?
    ORDER BY r.id DESC
    """, (session["user"],))

    requests = cur.fetchall()
    con.close()

    return render_template("my_requests.html", requests=requests)

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():

    msg = ""
    form_data = {}
    field_errors = {}

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user_captcha = request.form.get("captcha", "").strip()
        form_data = {"username": username}

        if user_captcha != session.get("captcha_text"):
            field_errors["captcha"] = "Wrong CAPTCHA"
            msg = "Wrong CAPTCHA ❌"
            session["captcha_text"] = generate_captcha()
            return render_template("login.html", msg="", captcha=session["captcha_text"], form_data=form_data, field_errors=field_errors)

        con = sqlite3.connect("users.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()
        con.close()

        if user:
            session["user"] = username
            session.pop("captcha_text", None)
            notify("Welcome 👋")
            return redirect("/")
        else:
            field_errors["password"] = "Invalid username or password"
            msg = "Invalid Credentials ❌"

    session["captcha_text"] = generate_captcha()
    return render_template("login.html", msg="", captcha=session["captcha_text"], form_data=form_data, field_errors=field_errors)

#---------------------Register-------------------------


@app.route("/register", methods=["GET", "POST"])
def register():

    msg = ""

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        phone = request.form.get("phone")
        address = request.form.get("address")
        user_captcha = request.form.get("captcha")

        if user_captcha != session.get("register_captcha_text"):
            msg = "Wrong CAPTCHA ❌"
            session["register_captcha_text"] = generate_captcha()
            return render_template("register.html", msg=msg, captcha=session["register_captcha_text"])

        # ❌ basic validation
        if not all([username, password, email, phone, address]):
            msg = "All fields required ⚠️"
            session["register_captcha_text"] = generate_captcha()
            return render_template("register.html", msg=msg, captcha=session["register_captcha_text"])

        con = sqlite3.connect("users.db")
        cur = con.cursor()

        try:
            cur.execute("""
                INSERT INTO users (username, password, email, phone, address)
                VALUES (?, ?, ?, ?, ?)
            """, (username, password, email, phone, address))

            con.commit()
            msg = "Registered successfully ✅ Please login"

        except sqlite3.IntegrityError as e:

            if "email" in str(e).lower():
                msg = "Email already registered ❌"
            else:
                msg = "Username already exists ❌"

        con.close()
        session["register_captcha_text"] = generate_captcha()
        return render_template("register.html", msg=msg, captcha=session["register_captcha_text"])

    session["register_captcha_text"] = generate_captcha()
    return render_template("register.html", msg=msg, captcha=session["register_captcha_text"])

#----------OTP PAGE------------------
#--------send otp--------------
@app.route("/send_otp", methods=["POST"])
def send_otp():

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    address = request.form.get("address", "").strip()
    user_captcha = request.form.get("captcha", "").strip()
    form_data = {
        "username": username,
        "address": address,
        "phone": phone,
        "email": email
    }
    field_errors = {}

    if user_captcha != session.get("register_captcha_text"):
        field_errors["captcha"] = "Wrong CAPTCHA"
        session["register_captcha_text"] = generate_captcha()
        return render_template("register.html", msg="", captcha=session["register_captcha_text"], form_data=form_data, field_errors=field_errors)
        return render_template("register.html", msg="Wrong CAPTCHA ❌", captcha=session["register_captcha_text"])

    if not all([username, password, email, phone, address]):
        for field_name, value in {
            "username": username,
            "password": password,
            "address": address,
            "phone": phone,
            "email": email
        }.items():
            if not value:
                field_errors[field_name] = "This field is required"
                form_data[field_name] = ""
                break
        session["register_captcha_text"] = generate_captcha()
        return render_template("register.html", msg="", captcha=session["register_captcha_text"], form_data=form_data, field_errors=field_errors)
        notify("All fields required ⚠️")
        return redirect("/register")

    # CHECK EXISTING USERNAME OR EMAIL
    con = sqlite3.connect("users.db")
    cur = con.cursor()

    cur.execute("SELECT username FROM users WHERE username=?", (username,))
    username_exists = cur.fetchone()

    cur.execute("SELECT email FROM users WHERE email=?", (email,))
    email_exists = cur.fetchone()

    con.close()

    if username_exists and email_exists:
        field_errors["username"] = "Username already exists"
        field_errors["email"] = "Email already registered"
        form_data["username"] = ""
        form_data["email"] = ""
        session["register_captcha_text"] = generate_captcha()
        return render_template("register.html", msg="", captcha=session["register_captcha_text"], form_data=form_data, field_errors=field_errors)
        return render_template(
            "register.html",
            msg="Username and Email already already exist ❌"
        )
    elif username_exists:
        field_errors["username"] = "Username already exists"
        form_data["username"] = ""
        session["register_captcha_text"] = generate_captcha()
        return render_template("register.html", msg="", captcha=session["register_captcha_text"], form_data=form_data, field_errors=field_errors)
        return render_template(
            "register.html",
            msg="Username already exists ❌"
        )
    elif email_exists:
        field_errors["email"] = "Email already registered"
        form_data["email"] = ""
        session["register_captcha_text"] = generate_captcha()
        return render_template("register.html", msg="", captcha=session["register_captcha_text"], form_data=form_data, field_errors=field_errors)
        return render_template(
            "register.html",
            msg="Email already registered ❌"
        )

    session["temp_user"] = username
    session["temp_password"] = password
    session["temp_email"] = email
    session["temp_phone"] = phone
    session["temp_address"] = address

    otp = random.randint(1000, 9999)
    session["otp"] = otp

    send_email_otp(email, otp)
    print("OTP:", otp)

    return redirect("/otp_page")

@app.route("/otp_page")
def otp_page():
    if "otp" not in session:
        return redirect("/register")
    return render_template("otp.html")

# -------- VERIFY REGISTER OTP --------
@app.route("/verify_register_otp", methods=["POST"])
def verify_register_otp():

    entered_otp = request.form.get("otp")

    if str(entered_otp) != str(session.get("otp")):
        notify("Wrong OTP ❌")
        return redirect("/otp_page")

    username = session.get("temp_user")
    password = session.get("temp_password")
    email = session.get("temp_email")
    phone = session.get("temp_phone")
    address = session.get("temp_address")

    con = sqlite3.connect("users.db")
    cur = con.cursor()

    try:

        cur.execute("""
        INSERT INTO users (username, password, email, phone, address)
        VALUES (?, ?, ?, ?, ?)
        """, (username, password, email, phone, address))

        con.commit()

    except sqlite3.IntegrityError as e:

        con.close()
        if "email" in str(e).lower():
            notify("Email already registered ❌")
        else:
            notify("Username already exists ❌")
        return redirect("/register")

    con.close()

    # clear temp session
    session.pop("otp", None)
    session.pop("temp_user", None)
    session.pop("temp_password", None)
    session.pop("temp_email", None)
    session.pop("temp_phone", None)
    session.pop("temp_address", None)

    notify("Registration Successful ✅")
    return redirect("/login")

#----VERIFY OTP-------------
@app.route("/reset_otp", methods=["GET", "POST"])
def reset_otp():

    if request.method == "POST":
        user_otp = request.form.get("otp")

        if str(session.get("fp_otp")) == str(user_otp):
            return redirect("/new_password")
        else:
            notify("Wrong OTP ❌")
            return redirect("/reset_otp")

    return render_template("reset_otp.html")

#-------------FORGOT PASSWORD---------------------
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":
        email = request.form.get("email")

        con = sqlite3.connect("users.db")
        cur = con.cursor()
        cur.execute("SELECT username FROM users WHERE email=?", (email,))
        user = cur.fetchone()
        con.close()

        if not user:
            notify("Email not registered ❌")
            return redirect("/forgot_password")

        otp = random.randint(1000, 9999)
        session["fp_otp"] = otp
        session["fp_email"] = email

        send_email_otp(email, otp)
        return redirect("/reset_otp")

    return render_template("forgot_password.html")

#------------------------------------SET NEW PASSWORD-----------------------

@app.route("/new_password", methods=["GET", "POST"])
def new_password():

    if request.method == "POST":

        new_pass = request.form.get("password")

        con = sqlite3.connect("users.db")
        cur = con.cursor()

        cur.execute("""
        UPDATE users SET password=? WHERE email=?
        """, (new_pass, session.get("fp_email")))

        con.commit()
        con.close()

        session.pop("fp_otp", None)
        session.pop("fp_email", None)

        notify("Password updated ✅ Please login")
        return redirect("/login")

    return render_template("new_password.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- ADMIN ----------------
@app.route('/admin', methods=['GET','POST'])
def admin():
    error = ""
    username = ""

    if request.method == 'POST':
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == "amogh" and password == "amogh#196":
            session["admin"] = True
            return redirect("/admin_dashboard")

        error = "Invalid admin username or password"

    return render_template("admin.html", error=error, username=username)

# ---------------- ADMIN DASHBOARD ----------------
@app.route('/admin_dashboard')
def admin_dashboard():

    if "admin" not in session:
        return redirect("/admin")

    con = sqlite3.connect("products.db")
    cur = con.cursor()

    cur.execute("SELECT * FROM products")
    products = cur.fetchall()

    cur.execute("""
    SELECT r.id, r.username, p.name, r.message, r.status
    FROM product_requests r
    JOIN products p ON r.product_id = p.id
    """)
    requests = cur.fetchall()

    # Get report statistics
    cur.execute("SELECT COUNT(*) FROM products")
    total_products = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM product_requests")
    total_requests = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM product_requests WHERE status='Pending'")
    pending_requests = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM product_requests WHERE status='Approved'")
    approved_requests = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM product_requests WHERE status='Rejected'")
    rejected_requests = cur.fetchone()[0]

    # Get most requested products
    cur.execute("""
    SELECT p.name, COUNT(r.id) as request_count
    FROM products p
    LEFT JOIN product_requests r ON p.id = r.product_id
    GROUP BY p.id, p.name
    ORDER BY request_count DESC
    LIMIT 5
    """)
    popular_products = cur.fetchall()

    # Get users with most requests, only including registered users
    cur.execute("ATTACH DATABASE 'users.db' AS users_db")
    cur.execute("""
    SELECT r.username, COUNT(r.id) as request_count
    FROM product_requests r
    JOIN users_db.users u ON r.username = u.username
    GROUP BY r.username
    ORDER BY request_count DESC
    LIMIT 5
    """)
    active_users = cur.fetchall()
    cur.execute("DETACH DATABASE users_db")

    con.close()

    # Get total users from users.db
    con_users = sqlite3.connect("users.db")
    cur_users = con_users.cursor()
    cur_users.execute("SELECT COUNT(*) FROM users")
    total_users = cur_users.fetchone()[0]
    con_users.close()

    return render_template("admin_dashboard.html", 
                         products=products, 
                         requests=requests,
                         total_users=total_users,
                         total_products=total_products,
                         total_requests=total_requests,
                         pending_requests=pending_requests,
                         approved_requests=approved_requests,
                         rejected_requests=rejected_requests,
                         popular_products=popular_products,
                         active_users=active_users)

#-----------------approve and reject requests-------------------

@app.route('/approve_request/<int:rid>', methods=['POST'])
def approve_request(rid):
    if "admin" not in session:
        return redirect("/admin")

    con = sqlite3.connect("products.db")
    cur = con.cursor()
    cur.execute("UPDATE product_requests SET status='Approved' WHERE id=?", (rid,))
    con.commit()
    con.close()

    notify("Request Approved ✅")
    return redirect("/admin_dashboard")


@app.route('/reject_request/<int:rid>', methods=['POST'])
def reject_request(rid):
    if "admin" not in session:
        return redirect("/admin")

    con = sqlite3.connect("products.db")
    cur = con.cursor()
    cur.execute("UPDATE product_requests SET status='Rejected' WHERE id=?", (rid,))
    con.commit()
    con.close()

    notify("Request Rejected ❌")
    return redirect("/admin_dashboard")

#-------------------submit review--------------------

@app.route("/submit_review/<int:pid>", methods=["POST"])
def submit_review(pid):

    if "user" not in session:
        return redirect("/login")

    rating = request.form.get("rating")
    comment = request.form.get("comment")

    if not rating or not comment:
        notify("Review cannot be empty ⚠️")
        return redirect(f"/product/{pid}")

    con = sqlite3.connect("products.db")
    cur = con.cursor()

    cur.execute("""
        INSERT INTO reviews (username, rating, comment, product_id)
        VALUES (?, ?, ?, ?)
    """, (session["user"], rating, comment, pid))

    con.commit()
    con.close()

    notify("Review submitted ⭐")
    return redirect(f"/product/{pid}")

#------------------------ABOUT US---------
@app.route("/about")
def about():
    return render_template("about.html")


# ---------------- HISTORY ----------------
@app.route("/history")
def history():

    if "user" not in session:
        return redirect("/login")

    con = sqlite3.connect("products.db")
    cur = con.cursor()

    cur.execute("""
    SELECT DISTINCT p.*
    FROM products p
    JOIN user_history h ON p.id = h.product_id
    WHERE h.username=?
    ORDER BY h.id DESC
    """, (session["user"],))

    products = cur.fetchall()
    con.close()

    return render_template("history.html", products=products)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
