/**
 * Toast Notification System
 * Provides beautiful toast notifications as a replacement for alert() calls
 */

// Prevent duplicate declarations
if (typeof ToastSystem === 'undefined') {
    class ToastSystem {
    constructor() {
        this.container = null;
        this.toasts = new Set();
        this.init();
    }

    init() {
        // Create toast container if it doesn't exist
        if (!document.querySelector('.toast-container')) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        } else {
            this.container = document.querySelector('.toast-container');
        }
    }

    /**
     * Show a toast notification
     * @param {string} message - The message to display
     * @param {string} type - Toast type: 'success', 'error', 'warning', 'info'
     * @param {Object} options - Additional options
     */
    show(message, type = 'info', options = {}) {
        const {
            title = this.getDefaultTitle(type),
            duration = this.getDefaultDuration(type),
            persistent = false,
            allowHtml = false
        } = options;

        const toast = this.createToast(message, type, title, allowHtml);
        this.container.appendChild(toast);
        this.toasts.add(toast);

        // Trigger animation
        requestAnimationFrame(() => {
            toast.classList.add('show');
        });

        // Auto-dismiss unless persistent
        if (!persistent && duration > 0) {
            this.startProgressBar(toast, duration);
            setTimeout(() => {
                this.hide(toast);
            }, duration);
        }

        return toast;
    }

    createToast(message, type, title, allowHtml) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        const icon = this.getIcon(type);
        
        toast.innerHTML = `
            <div class="toast-header">
                <div class="toast-icon">${icon}</div>
                <h6 class="toast-title">${this.escapeHtml(title)}</h6>
                <button class="toast-close" type="button" aria-label="Close">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
            <div class="toast-body">${allowHtml ? message : this.escapeHtml(message)}</div>
            <div class="toast-progress"></div>
        `;

        // Add close event listener
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => {
            this.hide(toast);
        });

        // Add click to dismiss (optional)
        toast.addEventListener('click', (e) => {
            if (e.target === toast || e.target.classList.contains('toast-body')) {
                this.hide(toast);
            }
        });

        return toast;
    }

    hide(toast) {
        if (!toast || toast.classList.contains('hiding')) return;

        toast.classList.add('hiding');
        toast.classList.remove('show');

        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
            this.toasts.delete(toast);
        }, 300);
    }

    startProgressBar(toast, duration) {
        const progressBar = toast.querySelector('.toast-progress');
        if (!progressBar) return;

        progressBar.style.width = '100%';
        progressBar.style.transition = `width ${duration}ms linear`;
        
        requestAnimationFrame(() => {
            progressBar.style.width = '0%';
        });
    }

    getIcon(type) {
        const icons = {
            success: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="20,6 9,17 4,12"></polyline>
                      </svg>`,
            error: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                     <circle cx="12" cy="12" r="10"></circle>
                     <line x1="15" y1="9" x2="9" y2="15"></line>
                     <line x1="9" y1="9" x2="15" y2="15"></line>
                   </svg>`,
            warning: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                       <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                       <line x1="12" y1="9" x2="12" y2="13"></line>
                       <line x1="12" y1="17" x2="12.01" y2="17"></line>
                     </svg>`,
            info: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="16" x2="12" y2="12"></line>
                    <line x1="12" y1="8" x2="12.01" y2="8"></line>
                  </svg>`
        };
        return icons[type] || icons.info;
    }

    getDefaultTitle(type) {
        const titles = {
            success: 'Success',
            error: 'Error',
            warning: 'Warning',
            info: 'Information'
        };
        return titles[type] || 'Notification';
    }

    getDefaultDuration(type) {
        const durations = {
            success: 4000,
            error: 6000,
            warning: 5000,
            info: 4000
        };
        return durations[type] || 4000;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Convenience methods
    success(message, options = {}) {
        return this.show(message, 'success', options);
    }

    error(message, options = {}) {
        return this.show(message, 'error', options);
    }

    warning(message, options = {}) {
        return this.show(message, 'warning', options);
    }

    info(message, options = {}) {
        return this.show(message, 'info', options);
    }

    // Clear all toasts
    clear() {
        this.toasts.forEach(toast => this.hide(toast));
    }
}

// Create global instance only if it doesn't exist
if (!window.toast) {
    window.toast = new ToastSystem();
}
}

// Legacy alert() replacement function
window.showToast = function(message, type = 'info', options = {}) {
    return window.toast.show(message, type, options);
};

// Enhanced replacement functions for common patterns
window.showSuccess = function(message, options = {}) {
    return window.toast.success(message, options);
};

window.showError = function(message, options = {}) {
    return window.toast.error(message, options);
};

window.showWarning = function(message, options = {}) {
    return window.toast.warning(message, options);
};

window.showInfo = function(message, options = {}) {
    return window.toast.info(message, options);
};

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.toast.init();
    });
} else {
    window.toast.init();
}
