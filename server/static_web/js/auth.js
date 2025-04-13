// Auth state management
let currentUser = null;
const authCallbacks = [];

function onAuthStateChanged(callback) {
    authCallbacks.push(callback);
    if (currentUser) {
        callback(currentUser);
    }
}

function updateAuthState(user) {
    currentUser = user;
    authCallbacks.forEach(callback => callback(user));
}

// Check for auth callback in URL
function handleAuthCallback() {
    const hash = window.location.hash;
    if (hash.startsWith('#auth-callback')) {
        const params = new URLSearchParams(hash.substring(hash.indexOf('?')));
        const token = params.get('token');
        if (token) {
            localStorage.setItem('access_token', token);
            window.location.hash = '#';
            checkAuth();
        }
    }
}

// Check authentication status
async function checkAuth() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        updateAuthState(null);
        return;
    }

    try {
        const response = await fetch('/api/auth/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (response.ok) {
            const user = await response.json();
            updateAuthState(user);
        } else {
            localStorage.removeItem('access_token');
            updateAuthState(null);
        }
    } catch (error) {
        console.error('Auth check failed:', error);
        updateAuthState(null);
    }
}

// Login with email/password
async function loginWithEmail(email, password) {
    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                'username': email,
                'password': password
            })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access_token);
            updateAuthState(data.user);
            return { success: true };
        } else {
            const error = await response.json();
            return { success: false, error: error.detail };
        }
    } catch (error) {
        console.error('Login failed:', error);
        return { success: false, error: 'Login failed. Please try again.' };
    }
}

// Sign up with email/password
async function signupWithEmail(email, password, name) {
    try {
        const response = await fetch('/auth/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email,
                password,
                name
            })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access_token);
            updateAuthState(data.user);
            return { success: true };
        } else {
            const error = await response.json();
            return { success: false, error: error.detail };
        }
    } catch (error) {
        console.error('Signup failed:', error);
        return { success: false, error: 'Signup failed. Please try again.' };
    }
}

// Logout
function logout() {
    localStorage.removeItem('access_token');
    updateAuthState(null);
}

// Initialize auth
document.addEventListener('DOMContentLoaded', () => {
    handleAuthCallback();
    checkAuth();
});
