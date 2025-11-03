/**
 * Common utility functions for all dashboard pages
 * Toast notifications, API helpers, and shared functionality
 */

// Toast notification system
let toastContainer = null;

function initToasts() {
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'fixed top-4 right-4 z-50 space-y-2';
        document.body.appendChild(toastContainer);
    }
}

function showToast(message, type = 'info', duration = 3000) {
    initToasts();
    
    const toast = document.createElement('div');
    toast.className = `
        flex items-center p-4 rounded-lg shadow-lg max-w-xs w-full
        transform transition-all duration-300 ease-in-out translate-x-full opacity-0
        ${type === 'success' ? 'bg-green-500 text-white' : ''}
        ${type === 'error' ? 'bg-red-500 text-white' : ''}
        ${type === 'warning' ? 'bg-yellow-500 text-white' : ''}
        ${type === 'info' ? 'bg-blue-500 text-white' : ''}
    `;
    
    const icon = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    }[type] || 'fas fa-info-circle';
    
    toast.innerHTML = `
        <i class="${icon} mr-3"></i>
        <span class="flex-1">${message}</span>
        <button onclick="this.parentElement.remove()" class="ml-3 opacity-75 hover:opacity-100">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    toastContainer.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-x-full', 'opacity-0');
    }, 100);
    
    // Auto remove
    setTimeout(() => {
        if (toast.parentElement) {
            toast.classList.add('translate-x-full', 'opacity-0');
            setTimeout(() => toast.remove(), 300);
        }
    }, duration);
}

// API Helper functions
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        credentials: 'include' // Include cookies for session
    };
    
    const response = await fetch(url, { ...defaultOptions, ...options });
    
    if (!response.ok) {
        if (response.status === 401) {
            // Unauthorized - redirect to login
            window.location.href = '/login';
            return;
        }
        
        const errorData = await response.json().catch(() => ({ message: 'Unknown error' }));
        throw new Error(errorData.message || `HTTP ${response.status}`);
    }
    
    return response.json();
}

// Authentication functions
async function checkAuth() {
    try {
        const response = await apiRequest('/api/auth/me');
        return response.data.user;
    } catch (error) {
        console.error('Auth check failed:', error);
        return null;
    }
}

async function logout() {
    try {
        await apiRequest('/api/auth/logout', { method: 'POST' });
        window.location.href = '/login';
    } catch (error) {
        console.error('Logout failed:', error);
        // Force redirect anyway
        window.location.href = '/login';
    }
}

// Format utilities
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatCurrency(amount) {
    if (amount === null || amount === undefined) return '৳0';
    return `৳${Number(amount).toFixed(0)}`;
}

function formatPhone(phone) {
    if (!phone) return 'N/A';
    
    // Format as +880 XX XXX XXXX
    if (phone.length === 11 && phone.startsWith('01')) {
        return `+880 ${phone.substring(1, 3)} ${phone.substring(3, 6)} ${phone.substring(6)}`;
    }
    
    return phone;
}

// Validation utilities
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    // Remove all non-digits
    const cleaned = phone.replace(/\D/g, '');
    
    // Check if it's a valid Bangladesh mobile number
    if (cleaned.startsWith('880')) {
        return cleaned.length === 13 && cleaned.substring(3, 5) === '01';
    } else if (cleaned.startsWith('01')) {
        return cleaned.length === 11;
    }
    
    return false;
}

// Loading states
function setButtonLoading(button, loading = true) {
    if (loading) {
        button.disabled = true;
        const originalText = button.innerHTML;
        button.dataset.originalText = originalText;
        button.innerHTML = `
            <div class="spinner mr-2"></div>
            Loading...
        `;
    } else {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText || 'Submit';
    }
}

// Custom confirmation dialogs - no browser prompts
function confirmAction(message, onConfirm, onCancel = null, options = {}) {
    const title = options.title || 'Confirm Action';
    const confirmText = options.confirmText || 'Confirm';
    const cancelText = options.cancelText || 'Cancel';
    const type = options.type || 'warning'; // success, error, warning, info
    
    showCustomConfirm({
        title,
        message,
        confirmText,
        cancelText,
        type,
        onConfirm,
        onCancel
    });
}

function showCustomConfirm(options) {
    // Remove existing modal if any
    const existingModal = document.getElementById('custom-confirm-modal');
    if (existingModal) {
        existingModal.remove();
    }
    
    const iconClass = {
        success: 'fas fa-check-circle text-green-500',
        error: 'fas fa-exclamation-circle text-red-500',
        warning: 'fas fa-exclamation-triangle text-yellow-500',
        info: 'fas fa-info-circle text-blue-500'
    }[options.type] || 'fas fa-exclamation-triangle text-yellow-500';
    
    const modal = document.createElement('div');
    modal.id = 'custom-confirm-modal';
    modal.className = 'fixed inset-0 z-50 overflow-y-auto';
    modal.innerHTML = `
        <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>
            <span class="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>
            <div class="relative inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
                <div class="sm:flex sm:items-start">
                    <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full sm:mx-0 sm:h-10 sm:w-10">
                        <i class="${iconClass} text-2xl"></i>
                    </div>
                    <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                        <h3 class="text-lg leading-6 font-medium text-gray-900">${options.title}</h3>
                        <div class="mt-2">
                            <p class="text-sm text-gray-500">${options.message}</p>
                        </div>
                    </div>
                </div>
                <div class="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                    <button type="button" class="confirm-btn w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm">
                        ${options.confirmText}
                    </button>
                    <button type="button" class="cancel-btn mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:w-auto sm:text-sm">
                        ${options.cancelText}
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add event listeners
    const confirmBtn = modal.querySelector('.confirm-btn');
    const cancelBtn = modal.querySelector('.cancel-btn');
    const overlay = modal.querySelector('.bg-gray-500');
    
    function closeModal() {
        modal.remove();
    }
    
    confirmBtn.addEventListener('click', () => {
        closeModal();
        if (options.onConfirm) {
            options.onConfirm();
        }
    });
    
    cancelBtn.addEventListener('click', () => {
        closeModal();
        if (options.onCancel) {
            options.onCancel();
        }
    });
    
    overlay.addEventListener('click', () => {
        closeModal();
        if (options.onCancel) {
            options.onCancel();
        }
    });
}

// Custom alert function - no browser alerts
function showAlert(message, type = 'info', title = null) {
    const alertTitle = title || {
        success: 'Success',
        error: 'Error', 
        warning: 'Warning',
        info: 'Information'
    }[type] || 'Alert';
    
    showCustomConfirm({
        title: alertTitle,
        message,
        confirmText: 'OK',
        cancelText: '',
        type,
        onConfirm: () => {},
        onCancel: null
    });
}

// Form utilities
function getFormData(form) {
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        // Handle checkboxes and multiple values
        if (data[key]) {
            if (Array.isArray(data[key])) {
                data[key].push(value);
            } else {
                data[key] = [data[key], value];
            }
        } else {
            data[key] = value;
        }
    }
    
    return data;
}

function resetForm(form) {
    form.reset();
    
    // Clear any error messages
    const errorElements = form.querySelectorAll('.error-message');
    errorElements.forEach(el => el.remove());
    
    // Reset field styles
    const fields = form.querySelectorAll('.form-input, .form-select, .form-textarea');
    fields.forEach(field => {
        field.classList.remove('border-red-500', 'border-green-500');
    });
}

// Table utilities
function sortTableData(data, column, direction = 'asc') {
    return [...data].sort((a, b) => {
        let aVal = a[column];
        let bVal = b[column];
        
        // Handle null/undefined values
        if (aVal === null || aVal === undefined) aVal = '';
        if (bVal === null || bVal === undefined) bVal = '';
        
        // Convert to strings for comparison
        aVal = String(aVal).toLowerCase();
        bVal = String(bVal).toLowerCase();
        
        if (direction === 'asc') {
            return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
        } else {
            return aVal > bVal ? -1 : aVal < bVal ? 1 : 0;
        }
    });
}

function filterTableData(data, filters) {
    return data.filter(item => {
        return Object.entries(filters).every(([key, value]) => {
            if (!value) return true; // Skip empty filters
            
            const itemValue = String(item[key] || '').toLowerCase();
            const filterValue = String(value).toLowerCase();
            
            return itemValue.includes(filterValue);
        });
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initToasts();
    
    // Add global error handler for unhandled promise rejections
    window.addEventListener('unhandledrejection', function(event) {
        console.error('Unhandled promise rejection:', event.reason);
        showToast('An unexpected error occurred', 'error');
    });
    
    // Add global error handler for JavaScript errors
    window.addEventListener('error', function(event) {
        console.error('JavaScript error:', event.error);
        // Don't show toast for every JS error as it might be annoying
    });
});

// Export for use in other scripts
window.utils = {
    showToast,
    apiRequest,
    checkAuth,
    logout,
    formatDate,
    formatDateTime,
    formatCurrency,
    formatPhone,
    validateEmail,
    validatePhone,
    setButtonLoading,
    confirmAction,
    showAlert,
    showCustomConfirm,
    getFormData,
    resetForm,
    sortTableData,
    filterTableData
};