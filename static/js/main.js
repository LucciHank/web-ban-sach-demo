// Main JavaScript for Trạm Sách

// Session management
function getSessionId() {
    let sessionId = localStorage.getItem('session_id');
    if (!sessionId) {
        sessionId = generateSessionId();
        localStorage.setItem('session_id', sessionId);
    }
    return sessionId;
}

function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// API Base URL
const API_BASE = '/api';

// Cart functions
let cartCount = 0;

async function updateCartCount() {
    const sessionId = getSessionId();
    try {
        const response = await fetch(`${API_BASE}/cart/?session_id=${sessionId}`);
        const data = await response.json();
        cartCount = data.items ? data.items.reduce((sum, item) => sum + item.quantity, 0) : 0;

        const badge = document.querySelector('.cart-badge');
        if (badge) {
            if (cartCount > 0) {
                badge.textContent = cartCount;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        }
    } catch (error) {
        console.error('Error updating cart count:', error);
    }
}

async function addToCart(bookId, quantity = 1) {
    const sessionId = getSessionId();
    try {
        const response = await fetch(`${API_BASE}/cart/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                book_id: bookId,
                quantity: quantity,
                session_id: sessionId
            })
        });

        if (response.ok) {
            const data = await response.json();
            // Lưu session_id nếu được trả về
            if (data.session_id) {
                localStorage.setItem('session_id', data.session_id);
            }
            await updateCartCount();
            showNotification('Đã thêm vào giỏ hàng', 'success');
            return true;
        } else {
            const error = await response.json();
            showNotification(error.detail || 'Có lỗi xảy ra', 'error');
            return false;
        }
    } catch (error) {
        console.error('Error adding to cart:', error);
        showNotification('Có lỗi xảy ra', 'error');
        return false;
    }
}

// Notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#34c759' : type === 'error' ? '#ff3b30' : '#0071e3'};
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Search functionality with autocomplete
let searchTimeout = null;
let currentSuggestions = [];

function setupSearch() {
    const searchInput = document.getElementById('search-input');
    const suggestionsDiv = document.getElementById('search-suggestions');

    if (!searchInput || !suggestionsDiv) return;

    // Search on Enter
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const query = searchInput.value.trim();
            if (query) {
                suggestionsDiv.classList.remove('show');
                window.location.href = `/category/all?q=${encodeURIComponent(query)}`;
            }
        }
    });

    // Autocomplete on input
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();

        if (searchTimeout) {
            clearTimeout(searchTimeout);
        }

        if (query.length < 2) {
            suggestionsDiv.classList.remove('show');
            return;
        }

        searchTimeout = setTimeout(async () => {
            try {
                const response = await fetch(`/api/search/?q=${encodeURIComponent(query)}&limit=5`);
                const data = await response.json();

                if (data.books && data.books.length > 0) {
                    currentSuggestions = data.books;
                    renderSuggestions(data.books);
                    suggestionsDiv.classList.add('show');
                } else {
                    suggestionsDiv.classList.remove('show');
                }
            } catch (error) {
                console.error('Search error:', error);
                suggestionsDiv.classList.remove('show');
            }
        }, 300);
    });

    // Hide suggestions when clicking outside
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !suggestionsDiv.contains(e.target)) {
            suggestionsDiv.classList.remove('show');
        }
    });
}

function renderSuggestions(books) {
    const suggestionsDiv = document.getElementById('search-suggestions');
    if (!suggestionsDiv) return;

    suggestionsDiv.innerHTML = '';

    books.forEach(book => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        item.onclick = () => {
            window.location.href = `/product/${book.id}`;
        };

        item.innerHTML = `
            <img src="${book.image_url || '/static/images/placeholder.jpg'}" alt="${book.title}" class="suggestion-item-image" onerror="this.src='/static/images/placeholder.jpg'">
            <div class="suggestion-item-info">
                <div class="suggestion-item-title">${book.title}</div>
                <div class="suggestion-item-author">${book.authors}</div>
            </div>
            <div class="suggestion-item-price">${BookStore.formatPrice(book.price_vnd)}</div>
        `;

        suggestionsDiv.appendChild(item);
    });
}

// Mobile menu toggle
function toggleMobileMenu() {
    const mobileNav = document.getElementById('mobile-nav');
    if (mobileNav) {
        mobileNav.classList.toggle('show');
    }
}

// Format price
function formatPrice(price) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(price);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('vi-VN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(date);
}

// User menu toggle
function toggleUserMenu() {
    const menu = document.getElementById('user-dropdown-menu');
    if (menu) {
        menu.classList.toggle('show');
    }
}

// Close user menu when clicking outside
document.addEventListener('click', (e) => {
    const userMenu = document.getElementById('user-menu');
    const dropdown = document.getElementById('user-dropdown-menu');
    if (userMenu && dropdown && !userMenu.contains(e.target)) {
        dropdown.classList.remove('show');
    }
});

// Check authentication status
async function checkAuth() {
    const token = localStorage.getItem('access_token');
    if (token) {
        try {
            const response = await fetch('/api/auth/me', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (response.ok) {
                const user = await response.json();
                updateUserMenu(user);
                return user;
            } else {
                localStorage.removeItem('access_token');
            }
        } catch (error) {
            console.error('Auth check error:', error);
        }
    }
    updateUserMenu(null); // Ensure logged-out state is shown
    return null;
}

// Update user menu based on auth status
// Update user menu based on auth status
function updateUserMenu(user) {
    const authButtons = document.getElementById('auth-buttons');
    const userMenu = document.getElementById('user-menu');
    const adminLink = document.getElementById('admin-link');
    const userAvatar = document.getElementById('user-avatar');

    // Elements to hide/show within dropdown (if reusing) - not needed with new layout split but kept for safety
    // Clean up old references

    if (user) {
        // Logged in: Show Avatar, Hide Buttons
        if (authButtons) authButtons.style.display = 'none';
        if (userMenu) userMenu.style.display = 'flex'; // Changed from block for better centering

        if (userAvatar) {
            userAvatar.innerHTML = `<i class="fa-regular fa-user"></i>`;
            userAvatar.title = user.email;
        }
        if (user.role === 'admin' && adminLink) {
            adminLink.style.display = 'flex';
        }
    } else {
        // Logged out: Show Buttons, Hide Avatar
        if (authButtons) authButtons.style.display = 'flex';
        if (userMenu) userMenu.style.display = 'none';
    }
}

// Logout function
function logout() {
    localStorage.removeItem('access_token');
    updateUserMenu(null);
    window.location.href = '/';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    updateCartCount();
    setupSearch();
    checkAuth();
});


// Add animation styles
const style = document.createElement('style');
style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
document.head.appendChild(style);


// Export for use in other scripts
window.BookStore = {
    getSessionId,
    addToCart,
    updateCartCount,
    formatPrice,
    formatDate,
    showNotification,
    checkAuth,
    updateUserMenu,
    logout
};

// Make functions global
window.toggleMobileMenu = toggleMobileMenu;

