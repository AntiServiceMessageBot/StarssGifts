const tg = window.Telegram.WebApp;
const user_id = tg.initDataUnsafe.user?.id || 123456;

let products = [];
let favorites = [];
let cart = [];

document.addEventListener('DOMContentLoaded', async () => {
    tg.expand();
    await loadCatalog();
    await loadFavorites();
    await loadCart();
});

async function loadCatalog() {
    const response = await fetch('/catalog');
    const data = await response.json();
    products = data.products;
    renderProducts(products, 'products-grid');
}

async function loadFavorites() {
    const response = await fetch(`/favorites/${user_id}`);
    const data = await response.json();
    favorites = data.favorites;
    renderProducts(favorites, 'favorites-grid', true);
}

async function loadCart() {
    const response = await fetch(`/cart/${user_id}`);
    const data = await response.json();
    cart = data.cart;
    renderCart(data.total);
}

function renderProducts(productsList, containerId, isFavorites = false) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';

    if (productsList.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">${isFavorites ? '⭐' : '📦'}</div>
                <p>${isFavorites ? 'В избранном пока пусто' : 'Каталог пуст'}</p>
            </div>
        `;
        return;
    }

    productsList.forEach(product => {
        const isFavorite = favorites.some(f => f.id === product.id);
        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `
            <div class="product-image">📦</div>
            <div class="product-name">${product.name}</div>
            <div class="product-price">${product.price} ₸</div>
            <div class="product-seller">${product.seller_name}</div>
            <div class="product-actions">
                <button class="action-btn" onclick="addToCart(${product.id})">🛒 В корзину</button>
                <button class="action-btn secondary" onclick="toggleFavorite(${product.id})">
                    ${isFavorite ? '❤️' : '🤍'}
                </button>
            </div>
        `;
        container.appendChild(card);
    });
}

function renderCart(total) {
    const container = document.getElementById('cart-items');
    container.innerHTML = '';

    if (cart.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🛒</div>
                <p>Корзина пуста</p>
            </div>
        `;
        document.getElementById('total-price').textContent = '0';
        return;
    }

    cart.forEach(item => {
        const cartItem = document.createElement('div');
        cartItem.className = 'cart-item';
        cartItem.innerHTML = `
            <div class="cart-item-info">
                <div class="cart-item-name">${item.name}</div>
                <div class="cart-item-price">${item.price} ₸ × ${item.quantity} = ${item.total} ₸</div>
            </div>
            <div class="cart-item-actions">
                <button class="quantity-btn" onclick="updateCart(${item.id}, -1)">-</button>
                <span>${item.quantity}</span>
                <button class="quantity-btn" onclick="updateCart(${item.id}, 1)">+</button>
                <button class="quantity-btn remove-btn" onclick="removeFromCart(${item.id})">✕</button>
            </div>
        `;
        container.appendChild(cartItem);
    });

    document.getElementById('total-price').textContent = total;
}

async function addToCart(productId) {
    await fetch('/cart/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id, product_id: productId, quantity: 1 })
    });
    await loadCart();
    tg.showPopup({ title: 'Успешно', message: 'Товар добавлен в корзину' });
}

async function removeFromCart(productId) {
    await fetch('/cart/remove', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id, product_id: productId })
    });
    await loadCart();
}

async function updateCart(productId, delta) {
    const item = cart.find(i => i.id === productId);
    if (item) {
        const newQuantity = item.quantity + delta;
        if (newQuantity <= 0) {
            await removeFromCart(productId);
        } else {
            await fetch('/cart/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id, product_id: productId, quantity: delta })
            });
            await loadCart();
        }
    }
}

async function toggleFavorite(productId) {
    const isFavorite = favorites.some(f => f.id === productId);
    const endpoint = isFavorite ? '/favorites/remove' : '/favorites/add';

    await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id, product_id: productId })
    });

    await loadFavorites();
    await loadCatalog();
}

function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    document.getElementById(sectionId).classList.add('active');
    event.target.classList.add('active');
}

function checkout() {
    if (cart.length === 0) {
        tg.showPopup({ title: 'Ошибка', message: 'Корзина пуста' });
        return;
    }

    tg.showPopup({
        title: 'Заказ оформлен',
        message: 'Спасибо за покупку! Ваш заказ скоро будет обработан.'
    });

    fetch('/cart/clear', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id })
    }).then(() => loadCart());
}