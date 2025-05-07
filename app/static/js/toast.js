/**
 * Toast notification system
 */
const Toast = {
    /**
     * Show a toast notification
     * @param {string} message - Message to display
     * @param {string} type - Type of toast (success, error, warning, info)
     * @param {number} duration - Duration in milliseconds
     */
    show: function(message, type = 'info', duration = 3000) {
        // Create toast container if it doesn't exist
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(container);
        }
        
        // Create toast element
        const toastId = 'toast-' + Date.now();
        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        // Create toast content
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        // Add toast to container
        container.appendChild(toast);
        
        // Initialize Bootstrap toast
        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: duration
        });
        
        // Show toast
        bsToast.show();
        
        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    },
    
    /**
     * Show a success toast
     * @param {string} message - Message to display
     * @param {number} duration - Duration in milliseconds
     */
    success: function(message, duration = 3000) {
        this.show(message, 'success', duration);
    },
    
    /**
     * Show an error toast
     * @param {string} message - Message to display
     * @param {number} duration - Duration in milliseconds
     */
    error: function(message, duration = 4000) {
        this.show(message, 'danger', duration);
    },
    
    /**
     * Show a warning toast
     * @param {string} message - Message to display
     * @param {number} duration - Duration in milliseconds
     */
    warning: function(message, duration = 3500) {
        this.show(message, 'warning', duration);
    },
    
    /**
     * Show an info toast
     * @param {string} message - Message to display
     * @param {number} duration - Duration in milliseconds
     */
    info: function(message, duration = 3000) {
        this.show(message, 'info', duration);
    }
};
