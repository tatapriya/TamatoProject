# 🍅 FreshTomato - Flask Application

A complete tomato selling platform built with Flask, Jinja2, and CSS. This application allows farmers to sell tomatoes directly to customers with admin oversight.

## Features

### 🔐 Authentication System
- **Multi-role login**: Farmer, Customer, and Admin roles
- **Registration system**: New users can register as farmers or customers
- **Admin approval**: Admins must approve new user registrations
- **Session management**: Secure user sessions with Flask

### 👨‍🌾 Farmer Features
- **Product management**: Upload and manage tomato products
- **Order handling**: View and manage incoming orders
- **Status updates**: Accept, reject, or mark orders as delivered
- **Dashboard**: View sales statistics and order summaries

### 🛒 Customer Features
- **Product browsing**: View all available tomato products
- **Shopping cart**: Add products to cart and manage quantities
- **Order tracking**: View order history and status
- **Checkout process**: Complete purchases and place orders

### 👨‍💼 Admin Features
- **User management**: Approve or reject new user registrations
- **System overview**: View platform statistics and metrics
- **Order monitoring**: Track all orders across the platform

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## 🎯 Usage Guide

### For Customers
1. **Register/Login**: Create an account or sign in as a customer
2. **Browse Products**: View available tomatoes from local farmers
3. **Add to Cart**: Select products and add them to your shopping cart
4. **Checkout**: Review cart and complete your purchase
5. **Track Orders**: Monitor your order status and delivery dates

### For Farmers
1. **Register/Login**: Create an account or sign in as a farmer
2. **Upload Products**: Add your tomato products with details and images
3. **Manage Orders**: View incoming orders and update their status
4. **Track Sales**: Monitor your sales statistics and revenue

### For Admins
1. **Login**: Use admin credentials (Username: Admin, Password: Admin)
2. **Review Requests**: Approve or reject new user registrations
3. **Monitor Platform**: View overall system statistics and metrics

## 📁 Project Structure

```
project/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # Jinja2 HTML templates
│   ├── base.html         # Base template with navigation
│   ├── landing.html      # Welcome/landing page
│   ├── login.html        # Login form
│   ├── register.html     # Registration form
│   ├── dashboard.html    # User dashboard
│   ├── customer_products.html    # Product browsing for customers
│   ├── farmer_products.html      # Product management for farmers
│   ├── upload_product.html       # Product upload form
│   ├── cart.html         # Shopping cart
│   ├── customer_orders.html      # Customer order history
│   ├── farmer_orders.html        # Farmer order management
│   └── admin_requests.html       # Admin user approval
└── static/               # Static assets
    └── index.css         # Custom CSS styles
```

## 🔧 Technical Details

### Backend (Python/Flask)
- **Flask Framework**: Web application framework
- **Session Management**: User authentication and state management
- **Data Storage**: In-memory data store (can be extended to use a database)
- **Role-based Access Control**: Different features for different user types

### Frontend (HTML/CSS)
- **Jinja2 Templates**: Server-side templating engine
- **Tailwind CSS**: Utility-first CSS framework (via CDN)
- **Responsive Design**: Mobile-friendly interface
- **Modern UI**: Clean and intuitive user interface

### Key Routes
- `/` - Landing page
- `/login` - User authentication
- `/register` - User registration
- `/dashboard` - User dashboard
- `/products` - Product browsing/management
- `/cart` - Shopping cart
- `/orders` - Order management
- `/admin_requests` - Admin user approval

## 🎨 Design Features

- **Gradient backgrounds**: Beautiful color schemes
- **Card-based layout**: Clean product and order displays
- **Status indicators**: Color-coded order and user status
- **Responsive navigation**: Role-based menu items
- **Flash messages**: User feedback and notifications

## 🔒 Security Features

- **Session-based authentication**: Secure user sessions
- **Role-based access control**: Different permissions for different roles
- **Input validation**: Form validation and sanitization
- **CSRF protection**: Built-in Flask security features

## 🚀 Future Enhancements

- **Database integration**: Replace in-memory storage with SQLite/PostgreSQL
- **File upload**: Allow farmers to upload product images
- **Payment integration**: Add payment processing
- **Email notifications**: Order status updates via email
- **Product reviews**: Customer rating and review system
- **Search and filtering**: Advanced product search
- **Inventory management**: Real-time stock tracking

## 🤝 Contributing

Feel free to contribute to this project by:
- Reporting bugs
- Suggesting new features
- Submitting pull requests
- Improving documentation

## 📄 License

This project is open source and available under the MIT License.

---

**Happy tomato selling! 🍅** 