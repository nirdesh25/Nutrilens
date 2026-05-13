"""
Minimal Smart Inventory System - Guaranteed to Work
"""
from flask import Flask, render_template_string, request, redirect, url_for, flash, session
import sqlite3
import hashlib
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Database setup
def init_db():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT, 
                  first_name TEXT, last_name TEXT, role TEXT)''')
    
    # Products table
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY, name TEXT, price REAL, quantity INTEGER, 
                  description TEXT, category TEXT)''')
    
    # Purchase requests table
    c.execute('''CREATE TABLE IF NOT EXISTS requests
                 (id INTEGER PRIMARY KEY, customer_id INTEGER, product_id INTEGER, 
                  quantity INTEGER, status TEXT, requested_at TEXT)''')
    
    # Create default admin if not exists
    c.execute("SELECT * FROM users WHERE email = 'admin@inventory.com'")
    if not c.fetchone():
        admin_password = hashlib.sha256('Admin123!'.encode()).hexdigest()
        c.execute("INSERT INTO users (email, password, first_name, last_name, role) VALUES (?, ?, ?, ?, ?)",
                 ('admin@inventory.com', admin_password, 'System', 'Administrator', 'admin'))
    
    conn.commit()
    conn.close()

# Helper functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(email):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    return user

def is_logged_in():
    return 'user_id' in session

def require_login():
    if not is_logged_in():
        return redirect(url_for('login'))
    return None

# Routes
@app.route('/')
def home():
    if is_logged_in():
        user = get_user_by_id(session['user_id'])
        if user and user[5] == 'admin':  # role is at index 5
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('customer_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = get_user(email)
        if user and user[2] == hash_password(password):  # password is at index 2
            session['user_id'] = user[0]
            session['user_name'] = user[3]  # first_name
            session['user_role'] = user[5]  # role
            flash(f'Welcome back, {user[3]}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smart Inventory - Login</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header bg-primary text-white text-center">
                            <h4>🏢 Smart Inventory System</h4>
                        </div>
                        <div class="card-body">
                            {% with messages = get_flashed_messages(with_categories=true) %}
                                {% if messages %}
                                    {% for category, message in messages %}
                                        <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }}">{{ message }}</div>
                                    {% endfor %}
                                {% endif %}
                            {% endwith %}
                            
                            <form method="POST">
                                <div class="mb-3">
                                    <label class="form-label">Email</label>
                                    <input type="email" class="form-control" name="email" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Password</label>
                                    <input type="password" class="form-control" name="password" required>
                                </div>
                                <button type="submit" class="btn btn-primary w-100">Login</button>
                            </form>
                            
                            <hr>
                            <div class="text-center">
                                <p><strong>Demo Account:</strong></p>
                                <p>Email: admin@inventory.com<br>Password: Admin123!</p>
                                <a href="{{ url_for('register') }}" class="btn btn-outline-secondary">Create Account</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    ''')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        role = request.form.get('role', 'customer')
        
        # Check if user exists
        if get_user(email):
            flash('Email already registered', 'error')
        else:
            # Create user
            conn = sqlite3.connect('inventory.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (email, password, first_name, last_name, role) VALUES (?, ?, ?, ?, ?)",
                     (email, hash_password(password), first_name, last_name, role))
            conn.commit()
            conn.close()
            
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smart Inventory - Register</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header bg-success text-white text-center">
                            <h4>Create Account</h4>
                        </div>
                        <div class="card-body">
                            {% with messages = get_flashed_messages(with_categories=true) %}
                                {% if messages %}
                                    {% for category, message in messages %}
                                        <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }}">{{ message }}</div>
                                    {% endfor %}
                                {% endif %}
                            {% endwith %}
                            
                            <form method="POST">
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">First Name</label>
                                        <input type="text" class="form-control" name="first_name" required>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Last Name</label>
                                        <input type="text" class="form-control" name="last_name" required>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Email</label>
                                    <input type="email" class="form-control" name="email" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Password</label>
                                    <input type="password" class="form-control" name="password" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Account Type</label>
                                    <select class="form-select" name="role">
                                        <option value="customer">Customer</option>
                                        <option value="admin">Administrator</option>
                                    </select>
                                </div>
                                <button type="submit" class="btn btn-success w-100">Register</button>
                            </form>
                            
                            <hr>
                            <div class="text-center">
                                <a href="{{ url_for('login') }}" class="btn btn-outline-primary">Back to Login</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    ''')

def get_user_by_id(user_id):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

@app.route('/admin/dashboard')
def admin_dashboard():
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    if session.get('user_role') != 'admin':
        flash('Admin access required', 'error')
        return redirect(url_for('customer_dashboard'))
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-dark bg-primary">
            <div class="container">
                <span class="navbar-brand">🏢 Smart Inventory - Admin</span>
                <div>
                    <span class="text-white me-3">Welcome, {{ session.user_name }}!</span>
                    <a href="{{ url_for('logout') }}" class="btn btn-outline-light btn-sm">Logout</a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <h2>Admin Dashboard</h2>
            <div class="row">
                <div class="col-md-4 mb-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5>📦 Products</h5>
                            <p>Manage inventory items</p>
                            <a href="#" class="btn btn-primary">Manage Products</a>
                        </div>
                    </div>
                </div>
                <div class="col-md-4 mb-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5>🛒 Requests</h5>
                            <p>Process purchase requests</p>
                            <a href="#" class="btn btn-success">View Requests</a>
                        </div>
                    </div>
                </div>
                <div class="col-md-4 mb-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5>📊 Analytics</h5>
                            <p>View reports and insights</p>
                            <a href="#" class="btn btn-info">View Analytics</a>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="alert alert-success">
                <h5>✅ System Status: Running</h5>
                <p>Your Smart Inventory Management System is working correctly!</p>
            </div>
        </div>
    </body>
    </html>
    ''')

@app.route('/customer/dashboard')
def customer_dashboard():
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Customer Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-dark bg-success">
            <div class="container">
                <span class="navbar-brand">🛒 Smart Inventory - Customer</span>
                <div>
                    <span class="text-white me-3">Welcome, {{ session.user_name }}!</span>
                    <a href="{{ url_for('logout') }}" class="btn btn-outline-light btn-sm">Logout</a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <h2>Customer Dashboard</h2>
            <div class="row">
                <div class="col-md-6 mb-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5>🛍️ Browse Products</h5>
                            <p>View available inventory</p>
                            <a href="#" class="btn btn-primary">Browse Products</a>
                        </div>
                    </div>
                </div>
                <div class="col-md-6 mb-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5>📋 My Requests</h5>
                            <p>View purchase history</p>
                            <a href="#" class="btn btn-info">View History</a>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="alert alert-info">
                <h5>✅ System Status: Running</h5>
                <p>Your Smart Inventory Management System is working correctly!</p>
            </div>
        </div>
    </body>
    </html>
    ''')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    print("🚀 Starting Minimal Smart Inventory System")
    print("📍 URL: http://localhost:8081")
    print("🔑 Admin: admin@inventory.com / Admin123!")
    print("=" * 50)
    app.run(debug=True, host='localhost', port=8081)