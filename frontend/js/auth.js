/**
 * Authentication Module for City Governance System
 * Handles user registration, login, logout, and Google OAuth
 */

const Auth = (function() {
    // Configuration
    const API_BASE_URL = 'http://localhost:8000/api/v1/auth';
    const GOOGLE_CLIENT_ID = 'YOUR_GOOGLE_CLIENT_ID'; // Replace with actual Google Client ID
    
    // Token storage keys
    const TOKEN_KEY = 'city_governance_token';
    const REFRESH_TOKEN_KEY = 'city_governance_refresh_token';
    const USER_KEY = 'city_governance_user';
    
    /**
     * Show alert message
     */
    function showAlert(message, type = 'error') {
        const container = document.getElementById('alert-container');
        if (!container) return;
        
        const alertColors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            info: 'bg-blue-500',
            warning: 'bg-yellow-500'
        };
        
        const alert = document.createElement('div');
        alert.className = `alert ${alertColors[type]} text-white px-4 py-3 rounded-lg mb-4`;
        alert.innerHTML = `
            <div class="flex items-center justify-between">
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-4 font-bold">×</button>
            </div>
        `;
        
        container.innerHTML = '';
        container.appendChild(alert);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }
    
    /**
     * Set loading state on button
     */
    function setButtonLoading(buttonId, loading) {
        const button = document.getElementById(buttonId);
        if (!button) return;
        
        if (loading) {
            button.disabled = true;
            button.innerHTML = `
                <svg class="animate-spin h-5 w-5 mx-auto" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
            `;
        } else {
            button.disabled = false;
        }
    }
    
    /**
     * Store authentication tokens
     */
    function storeTokens(accessToken, refreshToken, user) {
        localStorage.setItem(TOKEN_KEY, accessToken);
        localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
        localStorage.setItem(USER_KEY, JSON.stringify(user));
    }
    
    /**
     * Get stored access token
     */
    function getToken() {
        return localStorage.getItem(TOKEN_KEY);
    }
    
    /**
     * Get stored user
     */
    function getUser() {
        const userStr = localStorage.getItem(USER_KEY);
        return userStr ? JSON.parse(userStr) : null;
    }
    
    /**
     * Clear authentication data
     */
    function clearAuth() {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(REFRESH_TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
    }
    
    /**
     * Check if user is authenticated
     */
    function isAuthenticated() {
        return !!getToken();
    }
    
    /**
     * Make authenticated API request
     */
    async function apiRequest(endpoint, options = {}) {
        const token = getToken();
        
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Request failed');
        }
        
        return data;
    }
    
    /**
     * Register new user
     */
    async function register(userData) {
        try {
            const response = await apiRequest('/register', {
                method: 'POST',
                body: JSON.stringify(userData)
            });
            
            // Store tokens and user data
            storeTokens(
                response.token.access_token,
                response.token.refresh_token,
                response.user
            );
            
            return response;
        } catch (error) {
            throw error;
        }
    }
    
    /**
     * Login user
     */
    async function login(email, password) {
        try {
            const response = await apiRequest('/login', {
                method: 'POST',
                body: JSON.stringify({ email, password })
            });
            
            // Store tokens and user data
            storeTokens(
                response.token.access_token,
                response.token.refresh_token,
                response.user
            );
            
            return response;
        } catch (error) {
            throw error;
        }
    }
    
    /**
     * Logout user
     */
    async function logout() {
        try {
            await apiRequest('/logout', {
                method: 'POST'
            });
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            clearAuth();
        }
    }
    
    /**
     * Google OAuth Login
     */
    async function googleLogin(idToken) {
        try {
            const response = await apiRequest('/google', {
                method: 'POST',
                body: JSON.stringify({ id_token: idToken })
            });
            
            // Store tokens and user data
            storeTokens(
                response.token.access_token,
                response.token.refresh_token,
                response.user
            );
            
            return response;
        } catch (error) {
            throw error;
        }
    }
    
    /**
     * Initialize Google Sign-In
     */
    function initGoogleSignIn(callback) {
        if (typeof google === 'undefined') {
            console.warn('Google Sign-In library not loaded');
            return;
        }
        
        google.accounts.id.initialize({
            client_id: GOOGLE_CLIENT_ID,
            callback: callback
        });
    }
    
    /**
     * Handle Google credential response
     */
    async function handleGoogleResponse(response) {
        try {
            setButtonLoading('google-login-btn', true);
            const authResponse = await googleLogin(response.credential);
            showAlert('Successfully signed in with Google!', 'success');
            
            // Redirect after short delay
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1000);
        } catch (error) {
            showAlert(error.message, 'error');
        } finally {
            setButtonLoading('google-login-btn', false);
        }
    }
    
    /**
     * Initialize login page
     */
    function initLoginPage() {
        const form = document.getElementById('login-form');
        
        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;
                
                setButtonLoading('login-btn', true);
                
                try {
                    await login(email, password);
                    showAlert('Login successful! Redirecting...', 'success');
                    
                    // Redirect to dashboard/home
                    setTimeout(() => {
                        window.location.href = 'index.html';
                    }, 1000);
                } catch (error) {
                    showAlert(error.message, 'error');
                    setButtonLoading('login-btn', false);
                    // Restore button text
                    document.getElementById('login-btn').innerHTML = 'Sign In';
                }
            });
        }
        
        // Google Sign-In
        initGoogleSignIn(handleGoogleResponse);
        
        const googleBtn = document.getElementById('google-login-btn');
        if (googleBtn) {
            googleBtn.addEventListener('click', () => {
                if (typeof google !== 'undefined') {
                    google.accounts.id.prompt();
                } else {
                    showAlert('Google Sign-In is not available. Please use email/password.', 'warning');
                }
            });
        }
    }
    
    /**
     * Initialize register page
     */
    function initRegisterPage() {
        const form = document.getElementById('register-form');
        const roleSelect = document.getElementById('role');
        const departmentField = document.getElementById('department-field');
        const passwordInput = document.getElementById('password');
        const confirmPasswordInput = document.getElementById('confirm-password');
        
        // Show/hide department field based on role
        if (roleSelect && departmentField) {
            roleSelect.addEventListener('change', (e) => {
                if (e.target.value === 'department_user') {
                    departmentField.classList.remove('hidden');
                    document.getElementById('department').required = true;
                } else {
                    departmentField.classList.add('hidden');
                    document.getElementById('department').required = false;
                }
            });
        }
        
        // Password strength indicator
        if (passwordInput) {
            passwordInput.addEventListener('input', (e) => {
                const password = e.target.value;
                const strengthBar = document.getElementById('password-strength');
                const hint = document.getElementById('password-hint');
                
                let strength = 0;
                const checks = {
                    length: password.length >= 8,
                    uppercase: /[A-Z]/.test(password),
                    lowercase: /[a-z]/.test(password),
                    number: /[0-9]/.test(password),
                    special: /[^A-Za-z0-9]/.test(password)
                };
                
                strength = Object.values(checks).filter(Boolean).length;
                
                const colors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-lime-500', 'bg-green-500'];
                const labels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
                
                strengthBar.className = `password-strength ${colors[strength - 1] || 'bg-gray-300'}`;
                strengthBar.style.width = `${(strength / 5) * 100}%`;
                
                if (password.length > 0) {
                    hint.textContent = labels[strength - 1] || 'Too Weak';
                } else {
                    hint.textContent = 'Must contain uppercase, lowercase, and number';
                }
            });
        }
        
        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const password = passwordInput.value;
                const confirmPassword = confirmPasswordInput.value;
                
                // Validate passwords match
                if (password !== confirmPassword) {
                    showAlert('Passwords do not match', 'error');
                    return;
                }
                
                const userData = {
                    email: document.getElementById('email').value,
                    password: password,
                    full_name: document.getElementById('full-name').value,
                    role: roleSelect.value
                };
                
                if (roleSelect.value === 'department_user') {
                    const dept = document.getElementById('department').value;
                    if (!dept) {
                        showAlert('Please select a department', 'error');
                        return;
                    }
                    userData.department = dept;
                }
                
                setButtonLoading('register-btn', true);
                
                try {
                    await register(userData);
                    showAlert('Registration successful! Redirecting...', 'success');
                    
                    // Redirect to dashboard/home
                    setTimeout(() => {
                        window.location.href = 'index.html';
                    }, 1000);
                } catch (error) {
                    showAlert(error.message, 'error');
                    setButtonLoading('register-btn', false);
                    // Restore button text
                    document.getElementById('register-btn').innerHTML = 'Create Account';
                }
            });
        }
        
        // Google Sign-In
        initGoogleSignIn(async (response) => {
            try {
                setButtonLoading('google-register-btn', true);
                const authResponse = await googleLogin(response.credential);
                showAlert('Successfully signed up with Google!', 'success');
                
                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 1000);
            } catch (error) {
                showAlert(error.message, 'error');
                setButtonLoading('google-register-btn', false);
            }
        });
        
        const googleBtn = document.getElementById('google-register-btn');
        if (googleBtn) {
            googleBtn.addEventListener('click', () => {
                if (typeof google !== 'undefined') {
                    google.accounts.id.prompt();
                } else {
                    showAlert('Google Sign-In is not available. Please use email/password.', 'warning');
                }
            });
        }
    }
    
    // Public API
    return {
        register,
        login,
        logout,
        googleLogin,
        getToken,
        getUser,
        isAuthenticated,
        clearAuth,
        apiRequest,
        initLoginPage,
        initRegisterPage,
        showAlert
    };
})();

// Make Auth available globally
window.Auth = Auth;
