// Page Navigation
// function showPage(pageId) {
    
//     const pages = document.querySelectorAll('.page');
//     pages.forEach(page => page.classList.remove('active'));
    
    
//     document.getElementById(pageId).classList.add('active');
    
    
//     const navLinks = document.querySelectorAll('nav a');
//     navLinks.forEach(link => link.classList.remove('active'));
//     document.getElementById('nav-' + pageId).classList.add('active');
// }

// Shopping Cart Functionality
let cart = [];

function addToCart(productName) {
    price = 0 // placeholder for future dynamic pricing
    cart.push({ name: productName, price: price });
    showNotification(`${productName} added to cart!`);
    console.log('Cart:', cart);
    updateCartCount();
}

function showNotification(message) {
    const notification = document.getElementById('cart-notification');
    const text = document.getElementById('notification-text');
    text.textContent = message;
    notification.style.display = 'block';
    
    notification.style.opacity = '0';
    notification.style.transform = 'translateX(100px)';
    
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
        notification.style.transition = 'all 0.3s ease';
    }, 10);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100px)';
        setTimeout(() => {
            notification.style.display = 'none';
        }, 300);
    }, 2700);
}

function updateCartCount() {
    console.log(`Cart contains ${cart.length} items`);
}

// Floating Particles Animation
function createParticle() {
    const particle = document.createElement('div');
    particle.className = 'particle';
    particle.style.left = Math.random() * 100 + 'vw';
    particle.style.animationDuration = (Math.random() * 3 + 3) + 's';
    particle.style.animationDelay = Math.random() * 2 + 's';
    
    const colors = ['#00d4ff', '#ff0080', '#00ff88'];
    particle.style.background = colors[Math.floor(Math.random() * colors.length)];
    
    document.getElementById('particles').appendChild(particle);
    
    setTimeout(() => {
        if (particle.parentNode) {
            particle.remove();
        }
    }, 8000);
}

// Dynamic background color shifting
let hue = 0;
function updateBackgroundColor() {
    hue = (hue + 0.5) % 360;
    document.body.style.background = `linear-gradient(135deg, 
        hsl(${hue}, 100%, 5%) 0%, 
        hsl(${(hue + 20) % 360}, 80%, 15%) 50%, 
        hsl(${(hue + 40) % 360}, 60%, 20%) 100%)`;
}

// Enhanced card interactions
function initializeCardEffects() {
    const cards = document.querySelectorAll('.feature-card, .product-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// Keyboard navigation
function handleKeyboardNavigation(e) {
    if (e.key >= '1' && e.key <= '5') {
        const pages = ['home', 'products', 'about', 'contact', 'account'];
        const pageIndex = parseInt(e.key) - 1;
        if (pageIndex < pages.length) {
            showPage(pages[pageIndex]);
        }
    }
}

// Smooth page transitions
function initializePageTransitions() {
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => {
        page.style.transition = 'opacity 0.3s ease-in-out';
    });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Wavelength Gaming Gear website loaded successfully!');
    
    // Initialize all interactive features
    initializeCardEffects();
    initializePageTransitions();
    
    // Initialize cart count display
    updateCartCount();
    
    // Start particle system
    setInterval(createParticle, 300);
    
    // Start background color animation
    setInterval(updateBackgroundColor, 100);
    
    // Add keyboard navigation
    document.addEventListener('keydown', handleKeyboardNavigation);
    
    // Add some welcome effects
    setTimeout(() => {
        console.log('🎮 Welcome to Wavelength Gaming Gear!');
        console.log('💡 Tip: Use number keys 1-5 for quick navigation');
    }, 1000);
});

// Utility functions for future development
const WavelengthGear = {
    // Cart management
    getCart: () => cart,
    clearCart: () => {
        cart = [];
        updateCartCount();
    },
    removeFromCart: (index) => {
        if (index >= 0 && index < cart.length) {
            const removed = cart.splice(index, 1)[0];
            showNotification(`${removed.name} removed from cart`);
            updateCartCount();
        }
    },
    
    // Page management
    getCurrentPage: () => {
        const activePage = document.querySelector('.page.active');
        return activePage ? activePage.id : null;
    },
    
    // Animation controls
    stopParticles: () => {
        clearInterval(window.particleInterval);
    },
    
    startParticles: () => {
        window.particleInterval = setInterval(createParticle, 300);
    }
};

// Make utility functions globally available
window.WavelengthGear = WavelengthGear;