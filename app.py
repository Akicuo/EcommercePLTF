import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure upload folders
UPLOAD_FOLDER = 'uploads'
PREVIEW_FOLDER = os.path.join(UPLOAD_FOLDER, 'previews')
DIGITAL_FOLDER = os.path.join(UPLOAD_FOLDER, 'digital')
os.makedirs(PREVIEW_FOLDER, exist_ok=True)
os.makedirs(DIGITAL_FOLDER, exist_ok=True)

# Import models
from models import User, Product, store

@login_manager.user_loader
def load_user(user_id):
    return store.get_user(user_id)

# Add context processor to make store available in all templates
@app.context_processor
def inject_store():
    return dict(store=store)

@app.route('/')
def index():
    featured_products = store.get_products_by_category()[:6]
    return render_template('index.html', products=featured_products)

@app.route('/products')
def product_list():
    category = request.args.get('category')
    search = request.args.get('search', '').lower()

    filtered_products = store.get_products_by_category(category) if category else store.get_products_by_category()
    if search:
        filtered_products = [p for p in filtered_products if search in p.name.lower()]

    categories = set(p.category for p in store.get_products_by_category())
    return render_template('products.html', products=filtered_products, categories=categories)

@app.route('/products/<int:product_id>')
def get_product(product_id):
    product = store.get_product(product_id)
    if product:
        return jsonify({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'image': product.preview_image,
            'category': product.category,
            'description': product.description,
            'file_type': product.file_type
        })
    return jsonify({'error': 'Product not found'}), 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = store.get_user_by_email(email)
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

        if store.get_user_by_email(email):
            flash('Email already registered')
            return redirect(url_for('register'))

        user_id = str(len(store.users) + 1)
        user = User(user_id, username, email, generate_password_hash(password))
        store.add_user(user)
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/create_product', methods=['POST'])
@login_required
def create_product():
    try:
        name = request.form['name']
        price = float(request.form['price'])
        category = request.form['category']
        description = request.form['description']
        file_type = request.form['file_type']

        preview_image = request.files.get('preview_image')
        digital_file = request.files.get('digital_file')
        additional_images = request.files.getlist('additional_images')

        if not digital_file:
            flash('Digital product file is required')
            return redirect(url_for('profile'))

        product_id = len(store.products) + 1
        preview_path = "https://via.placeholder.com/200"
        additional_image_paths = []

        if preview_image:
            filename = secure_filename(f"{product_id}_main_{preview_image.filename}")
            preview_image.save(os.path.join(PREVIEW_FOLDER, filename))
            preview_path = url_for('static', filename=f'uploads/previews/{filename}')

        for idx, image in enumerate(additional_images):
            if image:
                filename = secure_filename(f"{product_id}_additional_{idx}_{image.filename}")
                image.save(os.path.join(PREVIEW_FOLDER, filename))
                additional_image_paths.append(url_for('static', filename=f'uploads/previews/{filename}'))

        digital_filename = secure_filename(f"{product_id}_{digital_file.filename}")
        digital_file.save(os.path.join(DIGITAL_FOLDER, digital_filename))

        product = Product(
            id=product_id,
            name=name,
            price=price,
            seller_id=current_user.id,
            category=category,
            description=description,
            file_type=file_type,
            preview_image=preview_path,
            additional_images=additional_image_paths
        )

        store.add_product(product)
        flash('Product created successfully')
        return redirect(url_for('profile'))

    except Exception as e:
        logging.error(f"Error creating product: {str(e)}")
        flash('Error creating product')
        return redirect(url_for('profile'))

@app.route('/profile')
@login_required
def profile():
    user_orders = store.get_user_orders(current_user.id)
    seller_products = store.get_seller_products(current_user.id)
    return render_template('profile.html', orders=user_orders, seller_products=seller_products)

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

        order = store.create_order(current_user.id, cart_items)
        session['cart'] = {}
        flash('Order placed successfully!')
        return redirect(url_for('profile'))
    return render_template('checkout.html')

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    return render_template('admin.html', orders=store.orders.values(), users=store.users.values())

# Initialize admin user
admin = User('admin', 'admin', 'admin@example.com', generate_password_hash('admin123'), is_admin=True)
store.add_user(admin)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = store.get_product(product_id)
    if product is None:
        flash('Product not found')
        return redirect(url_for('product_list'))
    return render_template('product_detail.html', product=product)