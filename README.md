# Taranga Electronics – Smart Appliances Management System

A full-stack web application for managing and browsing smart home appliances, built with **Python Flask** and **SQLite**. Developed as a BCA 6th Semester client-based project.

---

## 🚀 Features

### Customer Side
- **Product Catalogue** — Browse 60+ smart appliances across 10 categories (Refrigerators, Washing Machines, ACs, TVs, Fans, Coolers, Mixers, Grinders, Microwave Ovens, Water Heaters)
- **Product Details** — Full specs, images, category-specific attributes (capacity, type, energy rating), in-stock status
- **Cart System** — Add/remove items, increase/decrease quantities, stock-limit enforcement
- **User Registration** — OTP-based email verification via Gmail SMTP, CAPTCHA protection
- **User Login** — Session-based authentication with CAPTCHA
- **Password Recovery** — Forgot password flow with OTP email verification
- **Product Requests** — Logged-in users can send availability requests for products
- **Reviews** — Star ratings (1–5) and written reviews per product
- **Browsing History** — Auto-tracked viewed products accessible via History page
- **Delivery Availability** — Location-based availability check (Sirsi service area)
- **About Page** — Store information, services, and contact details
- **Google Maps Embed** — Store location and directions

### Admin Panel
- **Secure Login** — Credentials protected, client-side CAPTCHA
- **Product Management** — Add products with category-specific fields and image upload; delete products
- **Customer Requests** — View, approve, or reject customer product requests
- **Reports Dashboard** — Statistics: total users, products, request counts by status, most requested products, most active users

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Flask |
| Database | SQLite (products.db, users.db) |
| Frontend | HTML5, CSS3, JavaScript (Vanilla) |
| Auth | Flask sessions, CAPTCHA |
| Email | Gmail SMTP (smtplib) |
| File Upload | Werkzeug `secure_filename` |

---

## 📁 Project Structure

```
smart-appliances-management-system/
├── app.py              # Main Flask application (all routes)
├── admin.py            # Admin DB setup script
├── init_db.py          # Legacy DB initialization reference
├── requirements.txt    # Python dependencies
├── products.db         # Products, requests, reviews, history
├── users.db            # User accounts
├── admin.db            # Admin table (reference)
├── templates/          # Jinja2 HTML templates (15 files)
│   ├── index.html          # Home page with category grid & product listing
│   ├── product_detail.html # Product detail, reviews, request form
│   ├── cart.html           # Shopping cart
│   ├── login.html          # User login with CAPTCHA
│   ├── register.html       # Registration with OTP flow
│   ├── otp.html            # OTP verification for registration
│   ├── forgot_password.html# Password recovery by email
│   ├── reset_otp.html      # OTP verification for password reset
│   ├── new_password.html   # New password form
│   ├── my_requests.html    # User's product requests
│   ├── history.html        # Browsing history
│   ├── admin.html          # Admin login
│   ├── admin_dashboard.html# Admin panel (Products/Requests/Reports tabs)
│   ├── about.html          # About page
│   └── dashboard.html      # Basic user dashboard stub
└── static/
    ├── taranga123.png      # Store hero image
    ├── style.css           # Global styles
    ├── page-transition.css # Page fade animations
    ├── page-transition.js  # Page transition controller
    ├── no-image.png        # Fallback image placeholder
    ├── cat/                # Category thumbnail images (11 files)
    └── products/           # Product images (60+ files)
```

---

## ⚡ Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the application
```bash
python app.py
```

### 3. Open in browser
```
http://127.0.0.1:5000
```

---

## 🔐 Credentials

### Admin Login (at `/admin`)
| Field | Value |
|-------|-------|
| Username | `amogh` |
| Password | `amogh#196` |

### Demo Users (at `/login`)
| Username | Notes |
|----------|-------|
| `demo1` | Regular user, Sirsi address (delivery available) |
| `demo2` | Regular user |
| `cust1` | Regular user |

---

## 🗄️ Database Schema

### `products.db`
- **products** — `id, name, category, brand, capacity, type, energy, price, seller, image, stock`
- **product_requests** — `id, username, product_id, message, status`
- **reviews** — `id, username, rating, comment, product_id`
- **user_history** — `id, username, product_id`

### `users.db`
- **users** — `id, username, password, address, phone, email`

---

## 📸 Screenshots

> Run the app and navigate to `http://127.0.0.1:5000` to see:
> - Home page with hero section and category cards
> - Product grid with live images and Add to Cart
> - Full product detail page with specs and reviews
> - Admin dashboard with tabbed interface

---

*© 2026 Taranga Electronics, Sirsi — Karnataka*
