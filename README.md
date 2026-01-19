# BookStore Demo Project

Welcome to the BookStore Demo, a modern, full-stack e-commerce web application built with FastAPI and SQLite. This project demonstrates a premium UI/UX design, admin management, and core e-commerce functionalities like shopping cart, checkout, and user authentication.

## 🚀 Features

*   **Premium UI Design**: A sleek, responsive user interface inspired by modern design principles (Apple-like aesthetics), featuring glassmorphism, smooth animations, and a dark-mode styled footer.
*   **Product Management**: Browse books by category, view detailed product pages with image galleries, and check stock status.
*   **Shopping Cart**: Fully functional cart with real-time updates, quantity management, and "Add to Cart" animations.
*   **Checkout System**: streamlined checkout process with form validation, multiple payment methods (COD, Bank Transfer), and shipping options.
*   **User Authentication**: Secure login and registration system with JWT-based sessions (simulated via localStorage and session cookies).
*   **Admin Dashboard**: A powerful admin interface built with `SQLAdmin` to manage Books, Categories, Orders, and Users. Features a custom dark theme.
*   **Search**: Real-time product search functionality.

## 🛠 Tech Stack

*   **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python) - High performance, easy to learn, fast to code, ready for production.
*   **Database**: [SQLite](https://www.sqlite.org/index.html) - Lightweight disk-based database.
*   **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/) - The Python SQL Toolkit and Object Relational Mapper.
*   **Admin UI**: [SQLAdmin](https://aminalaee.github.io/sqladmin/) - Admin interface for FastAPI.
*   **Frontend**:
    *   **HTML5/CSS3**: Custom styles with rigorous attention to detail.
    *   **JavaScript (Vanilla)**: No heavy frameworks, just pure, efficient JS for interactivity.
    *   **FontAwesome**: For vector icons.
    *   **Google Fonts**: "Outfit" and "Inter" for typography.

## 📂 Project Structure

```
web-ban-sach-demo/
├── app/
│   ├── admin/          # Admin panel configuration (auth, views)
│   ├── models/         # Database models (User, Book, Order, etc.)
│   ├── routers/        # API Endpoints (auth, cart, products, checkout)
│   ├── database.py     # Database connection and session handling
│   └── utils.py        # Helper functions (hashing, security)
├── static/
│   ├── css/            # Custom Stylesheets (style.css, admin_custom.css)
│   ├── images/         # Static assets (placeholders, logos)
│   └── js/             # Client-side logic (main.js)
├── templates/          # HTML Templates (Jinja2)
│   ├── index.html      # Homepage
│   ├── base.html       # Base layout (Header, Footer)
│   ├── product.html    # Product details
│   ├── cart.html       # Shopping cart
│   ├── checkout.html   # Checkout page
│   └── ...
├── scripts/            # Utility scripts (init db, create admin, migrations)
├── main.py             # Application entry point
├── bookstore.db        # SQLite Database file
└── requirements.txt    # Python dependencies
```

## ⚡ Quick Start

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/web-ban-sach-demo.git
    cd web-ban-sach-demo
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Initialize Database**:
    The database `bookstore.db` is automatically created on first run. To create an admin user:
    ```bash
    python scripts/create_admin.py
    ```

4.  **Run the Server**:
    ```bash
    python main.py
    ```
    The server will start at `http://localhost:8000`.

5.  **Access Admin Panel**:
    *   URL: `http://localhost:8000/admin`
    *   Login with the credentials created in step 3.

## 🔄 Core Flows

### 1. User Journey
*   **Home**: Landing page with featured books, best sellers, and new arrivals.
*   **Browse**: Users click categories or search to find books.
*   **Product Detail**: View book info, reviews, and add to cart.
*   **Cart**: Review items, update quantities.
*   **Checkout**: Enter shipping details -> Place Order (Guest or Logged in).

### 2. Admin Management
*   Admins log in to `/admin`.
*   **CRUD Operations**: Create, Read, Update, Delete Books, Categories, and monitor Orders.
*   **Image Handling**: Add image URLs for books and categories directly in the admin panel.

## 🎨 Design Philosophy

The project follows a "Luxury & Modern" aesthetic:
*   **Typography**: Clean sans-serif fonts for readability.
*   **Color Palette**: Minimalist black/white/gray base with a Vibrant Blue (`#0071e3`) accent.
*   **Spacing**: Generous whitespace (`var(--spacing-xl)`) to create a breathable layout.
*   **Feedback**: Interactive hover states and toast notifications for user actions.

---
© 2024 Trạm Sách Demo. All rights reserved.
