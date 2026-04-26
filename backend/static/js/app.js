/**
 * OutfitCheck AI — Core JavaScript Module
 * Handles auth state, API calls, toasts, and shared utilities
 */

const API_BASE = '';

// ─── Auth State ───
function getToken() {
    return localStorage.getItem('token');
}

function setToken(token) {
    localStorage.setItem('token', token);
}

function clearToken() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
}

function getUser() {
    const u = localStorage.getItem('user');
    return u ? JSON.parse(u) : null;
}

function setUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
}

function requireAuth() {
    if (!getToken()) {
        window.location.href = '/login';
        return false;
    }
    return true;
}

// ─── API Helper ───
async function api(endpoint, options = {}) {
    const token = getToken();
    const headers = { ...(options.headers || {}) };

    if (token) headers['Authorization'] = `Bearer ${token}`;
    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }

    const res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });

    if (res.status === 401) {
        clearToken();
        window.location.href = '/login';
        return null;
    }

    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Something went wrong' }));
        throw new Error(err.detail || 'Request failed');
    }

    return res.json();
}

// ─── Toast Notifications ───
function showToast(message, type = 'success') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `${type === 'success' ? '✓' : '✕'} ${message}`;
    container.appendChild(toast);

    setTimeout(() => { toast.remove(); }, 4000);
}

// ─── Loading Overlay ───
function showLoading(message = 'Loading...') {
    let overlay = document.querySelector('.loading-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `<div class="spinner"></div><p>${message}</p>`;
        document.body.appendChild(overlay);
    } else {
        overlay.querySelector('p').textContent = message;
    }
    overlay.classList.add('active');
}

function hideLoading() {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) overlay.classList.remove('active');
}

// ─── Category Icons ───
const CATEGORY_ICONS = {
    top: '👕', bottom: '👖', shoes: '👟', accessory: '👜',
    outerwear: '🧥', dress: '👗', default: '🏷️'
};

function getCategoryIcon(cat) {
    return CATEGORY_ICONS[cat] || CATEGORY_ICONS.default;
}

// ─── Update Nav Auth State ───
function updateNav() {
    const user = getUser();
    const authLinks = document.getElementById('auth-links');
    const appLinks = document.getElementById('app-links');
    if (user && authLinks) authLinks.style.display = 'none';
    if (user && appLinks) appLinks.style.display = 'flex';
    if (!user && authLinks) authLinks.style.display = 'flex';
    if (!user && appLinks) appLinks.style.display = 'none';

    const userSpan = document.getElementById('user-name');
    if (userSpan && user) userSpan.textContent = user.username;
}

// ─── Logout ───
async function logout() {
    try { await api('/api/auth/logout', { method: 'POST' }); } catch (e) {}
    clearToken();
    window.location.href = '/';
}

// Run on page load
document.addEventListener('DOMContentLoaded', updateNav);
