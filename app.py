from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import json
from datetime import datetime
import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/fresh_tomato'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('farmer', 'customer', 'admin'), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    registration_date = db.Column(db.Date)
    is_approved = db.Column(db.Boolean, default=False)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(255))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10,2), nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rating = db.Column(db.Integer, default=5)
    farmer = db.relationship('User', backref='products', foreign_keys=[farmer_id])

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Numeric(10,2), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    farmer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.Enum('pending', 'accepted', 'delivered', 'rejected'), default='pending')
    order_date = db.Column(db.Date)
    delivery_date = db.Column(db.Date)
    product = db.relationship('Product', backref='orders')
    customer = db.relationship('User', foreign_keys=[customer_id])
    farmer = db.relationship('User', foreign_keys=[farmer_id])

# Initialize data store
# data_store = DataStore() # This line is no longer needed as data is in DB

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('landing'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('landing'))
            if session['user']['role'] not in allowed_roles:
                flash('Access denied. Insufficient permissions.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def landing():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        # Simple authentication logic
        if role == 'admin':
            if username == 'Admin' and password == 'Admin':
                session['user'] = {'username': 'Admin', 'role': 'admin'}
                flash('Welcome Admin!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid admin credentials', 'error')
        else:
            # Check if user exists in the database
            user = User.query.filter_by(username=username, role=role).first()
            if not user:
                flash('User not found. Please register.', 'error')
                return render_template('login.html')
            # For demo purposes, accept any password for farmer/customer
            session['user'] = {'username': username, 'role': role}
            flash(f'Welcome {username}!', 'success')
            return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        phone = request.form.get('phone')
        address = request.form.get('address')

        # Prevent admin registration from the form
        if role == 'admin':
            flash('Admin registration is not allowed.', 'error')
            return render_template('register.html')

        # Add to pending users
        new_user = User(username=username, password=password, role=role, phone=phone, address=address, registration_date=datetime.now().date())
        db.session.add(new_user)
        db.session.commit()

        flash('Registration submitted! Please wait for admin approval.', 'success')
        return redirect(url_for('landing'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = session['user']
    
    # Get stats based on user role
    if user['role'] == 'admin':
        stats = {
            'total_products': Product.query.count(),
            'total_orders': Order.query.count(),
            'pending_users': User.query.filter_by(is_approved=False).count(),
            'total_revenue': sum(order.total_price for order in Order.query.filter_by(status='delivered'))
        }
    elif user['role'] == 'farmer':
        farmer_orders = Order.query.filter_by(farmer_id=User.query.filter_by(username=user['username']).first().id).all()
        stats = {
            'total_products': Product.query.filter_by(farmer_id=User.query.filter_by(username=user['username']).first().id).count(),
            'total_orders': len(farmer_orders),
            'pending_orders': len([o for o in farmer_orders if o.status == 'pending']),
            'total_revenue': sum(order.total_price for order in farmer_orders if order.status == 'delivered')
        }
    else:  # customer
        customer_orders = Order.query.filter_by(customer_id=User.query.filter_by(username=user['username']).first().id).all()
        stats = {
            'total_orders': len(customer_orders),
            'pending_orders': len([o for o in customer_orders if o.status == 'pending']),
            'total_spent': sum(order.total_price for order in customer_orders),
            'favorite_product': 'Organic Cherry Tomatoes'  # Demo data
        }
    
    return render_template('dashboard.html', user=user, stats=stats)

@app.route('/products')
@login_required
def products():
    user = session['user']
    if user['role'] == 'farmer':
        farmer = User.query.filter_by(username=user['username']).first()
        user_products = Product.query.filter_by(farmer_id=farmer.id).all()
        # Calculate remaining stock for each product
        products_with_stock = []
        for product in user_products:
            sold_qty = sum(
                order.quantity for order in Order.query.filter_by(product_id=product.id)
                .filter(Order.status.in_(['accepted', 'delivered']))
            )
            remaining = product.quantity - sold_qty
            products_with_stock.append({
                'id': product.id,
                'name': product.name,
                'image': product.image,
                'price': product.price,
                'rating': product.rating,
                'remaining': remaining
            })
        return render_template('farmer_products.html', user=user, products=products_with_stock)
    else:
        # For customers, pass the full Product objects
        all_products = Product.query.all()
        return render_template('customer_products.html', user=user, products=all_products)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_product', methods=['GET', 'POST'])
@login_required
@role_required(['farmer'])
def upload_product():
    if request.method == 'POST':
        name = request.form.get('name')
        quantity = int(request.form.get('quantity'))
        price = float(request.form.get('price'))
        file = request.files.get('image')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Ensure the uploads directory exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Store the relative path for use in templates
            image_path = f'uploads/{filename}'
            
            # Load model and predict
            classes = ['1', '2', '3', '4','5']
            model = load_model('tomato.h5')
            
            # predicting images    
            image = load_img(file_path, target_size=(224,224))
            image = img_to_array(image)
            image = image/255
            image = np.expand_dims(image, axis=0)
            result = np.argmax(model.predict(image))
            prediction = classes[result]
            
            new_product = Product(
                name=name,
                image=image_path,
                quantity=quantity,
                price=price,
                farmer_id=User.query.filter_by(username=session['user']['username']).first().id,
                rating=int(prediction)  # Set rating to prediction value
            )
            db.session.add(new_product)
            db.session.commit()

            flash('Product uploaded successfully!', 'success')
            return redirect(url_for('products'))
        else:
            flash('Invalid image file.', 'error')
            return redirect(request.url)

    return render_template('upload_product.html', user=session['user'])

@app.route('/cart')
@login_required
@role_required(['customer'])
def cart():
    # In a real app, cart would be stored in session or database
    # For demo, we'll use a simple cart in session
    cart_items = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', user=session['user'], cart_items=cart_items, total=total)

@app.route('/add_to_cart/<int:product_id>')
@login_required
@role_required(['customer'])
def add_to_cart(product_id):
    product = Product.query.get(product_id)
    if product:
        cart = session.get('cart', [])
        existing_item = next((item for item in cart if item['id'] == product_id), None)
        # Calculate total quantity in cart for this product
        cart_qty = existing_item['quantity'] if existing_item else 0
        if cart_qty + 1 > product.quantity:
            flash('Not enough stock available.', 'error')
            return redirect(url_for('products'))
        if existing_item:
            existing_item['quantity'] += 1
        else:
            cart.append({
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'image': product.image,
                'quantity': 1,
                'farmer': product.farmer.username
            })
        session['cart'] = cart
        flash('Product added to cart!', 'success')
    return redirect(url_for('products'))

@app.route('/remove_from_cart/<int:product_id>')
@login_required
@role_required(['customer'])
def remove_from_cart(product_id):
    cart = session.get('cart', [])
    cart = [item for item in cart if item['id'] != product_id]
    session['cart'] = cart
    flash('Product removed from cart!', 'info')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
@role_required(['customer'])
def checkout():
    cart_items = session.get('cart', [])
    if not cart_items:
        flash('Your cart is empty!', 'error')
        return redirect(url_for('cart'))

    if request.method == 'POST':
        # Here you would process payment details (for demo, just place order)
        for item in cart_items:
            new_order = Order(
                product_id=item['id'],
                quantity=item['quantity'],
                total_price=item['price'] * item['quantity'],
                customer_id=User.query.filter_by(username=session['user']['username']).first().id,
                farmer_id=Product.query.get(item['id']).farmer_id,
                status='pending',
                order_date=datetime.now().date()
            )
            db.session.add(new_order)
        session['cart'] = []
        db.session.commit()
        flash('Order placed successfully!', 'success')
        return redirect(url_for('orders'))

    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('checkout.html', user=session['user'], cart_items=cart_items, total=total)

@app.route('/orders')
@login_required
def orders():
    user = session['user']
    
    if user['role'] == 'farmer':
        user_orders = Order.query.filter_by(farmer_id=User.query.filter_by(username=user['username']).first().id).all()
        return render_template('farmer_orders.html', user=user, orders=user_orders)
    else:
        user_orders = Order.query.filter_by(customer_id=User.query.filter_by(username=user['username']).first().id).all()
        return render_template('customer_orders.html', user=user, orders=user_orders)

@app.route('/update_order_status/<int:order_id>', methods=['POST'])
@login_required
@role_required(['farmer'])
def update_order_status(order_id):
    new_status = request.form.get('status')
    delivery_date = request.form.get('delivery_date')
    
    order = Order.query.get(order_id)
    if order:
        # If marking as delivered and not already delivered, deduct quantity
        if new_status == 'delivered' and order.status != 'delivered':
            product = Product.query.get(order.product_id)
            if product:
                product.quantity = max(product.quantity - order.quantity, 0)
        order.status = new_status
        if delivery_date:
            order.delivery_date = datetime.strptime(delivery_date, '%Y-%m-%d').date()
        db.session.commit()
        flash('Order status updated!', 'success')
    
    return redirect(url_for('orders'))

@app.route('/admin_requests')
@login_required
@role_required(['admin'])
def admin_requests():
    pending_users = User.query.filter_by(is_approved=False).all()
    return render_template('admin_requests.html', user=session['user'], pending_users=pending_users)

@app.route('/approve_user/<int:user_id>')
@login_required
@role_required(['admin'])
def approve_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.is_approved = True
        db.session.commit()
        flash('User approved!', 'success')
    return redirect(url_for('admin_requests'))

@app.route('/reject_user/<int:user_id>')
@login_required
@role_required(['admin'])
def reject_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User rejected!', 'info')
    return redirect(url_for('admin_requests'))

@app.route('/remove_product/<int:product_id>')
@login_required
@role_required(['farmer'])  # Only farmers can access this route
def remove_product(product_id):
    product = Product.query.get(product_id)
    if product:
        # Check if the product belongs to the current farmer
        current_farmer = User.query.filter_by(username=session['user']['username']).first()
        if product.farmer_id == current_farmer.id:  # Only their own products
            # Delete the image file if it exists
            if product.image:
                try:
                    image_path = os.path.join('static', product.image)
                    if os.path.exists(image_path):
                        os.remove(image_path)
                except Exception as e:
                    print(f"Error deleting image file: {e}")
            
            # Delete the product from database
            db.session.delete(product)
            db.session.commit()
            flash('Product removed successfully!', 'success')
        else:
            flash('You can only remove your own products!', 'error')  # Security message
    else:
        flash('Product not found!', 'error')
    
    return redirect(url_for('products'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 