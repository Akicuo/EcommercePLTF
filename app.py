import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# In-memory storage
users = {}
products = {
    1: {"id": 1, "name": "Laptop", "price": 999.99, "category": "Electronics", "description": "High-performance laptop", "image": "https://via.placeholder.com/200"},
    2: {"id": 2, "name": "Smartphone", "price": 499.99, "category": "Electronics", "description": "Latest smartphone", "image": "https://via.placeholder.com/200"},
    3: {"id": 3, "name": "Headphones", "price": 99.99, "category": "Accessories", "description": "Wireless headphones", "image": "https://via.placeholder.com/200"}
}
orders = {}
order_counter = 1

class User(UserMixin):
    def __init__(self, id, username, email, password_hash, is_admin=False):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.is_admin = is_admin

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

@app.route('/')
def index():
    return render_template('index.html', products=list(products.values())[:3])

@app.route('/products')
def product_list():
    category = request.args.get('category')
    search = request.args.get('search', '').lower()
    
    filtered_products = products.values()
    if category:
        filtered_products = [p for p in filtered_products if p['category'] == category]
    if search:
        filtered_products = [p for p in filtered_products if search in p['name'].lower()]
    
    categories = set(p['category'] for p in products.values())
    return render_template('products.html', products=filtered_products, categories=categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = next((u for u in users.values() if u.email == email), None)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if any(u.email == email for u in users.values()):
            flash('Email already registered')
            return redirect(url_for('register'))
        
        user_id = str(len(users) + 1)
        user = User(user_id, username, email, generate_password_hash(password))
        users[user_id] = user
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        cart_items = session.get('cart', {})
        if not cart_items:
            flash('Your cart is empty')
            return redirect(url_for('cart'))
        
        global order_counter
        order = {
            'id': order_counter,
            'user_id': current_user.id,
            'items': cart_items,
            'status': 'pending'
        }
        orders[order_counter] = order
        order_counter += 1
        
        session['cart'] = {}
        flash('Order placed successfully!')
        return redirect(url_for('profile'))
    return render_template('checkout.html')

@app.route('/profile')
@login_required
def profile():
    user_orders = [order for order in orders.values() if order['user_id'] == current_user.id]
    return render_template('profile.html', orders=user_orders)

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    return render_template('admin.html', orders=orders.values(), users=users.values())

# Initialize admin user
admin = User('admin', 'admin', 'admin@example.com', generate_password_hash('admin123'), is_admin=True)
users['admin'] = admin
