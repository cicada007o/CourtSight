// BNS Legal Assistant - Base JavaScript Functions

// Global variables
let systemStatus = { ready_for_queries: false };

// Initialize base functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeBaseFeatures();
    checkInitialSystemStatus();
});

// Initialize base features
function initializeBaseFeatures() {
    // Add smooth scrolling to all anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
    
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Add loading states to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.type === 'submit' || this.hasAttribute('data-loading')) {
                addLoadingState(this);
            }
        });
    });
}

// Check initial system status
function checkInitialSystemStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            systemStatus = data;
            updateSystemStatusDisplay(data);
        })
        .catch(error => {
            console.error('Failed to check system status:', error);
            showSystemStatusAlert('Error checking system status', 'danger');
        });
}

// System status functions
function checkSystemStatus() {
    showSystemStatusAlert('Checking system status...', 'info', true);
    
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            systemStatus = data;
            displaySystemStatusModal(data);
            hideSystemStatusAlert();
        })
        .catch(error => {
            console.error('Error checking system status:', error);
            showSystemStatusAlert('Failed to check system status', 'danger');
        });
}

function refreshSystemStatus() {
    const modalContent = document.getElementById('system-status-content');
    if (modalContent) {
        modalContent.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Refreshing system status...</p>
            </div>
        `;
    }
    
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            systemStatus = data;
            displaySystemStatusModal(data);
        })
        .catch(error => {
            console.error('Error refreshing system status:', error);
            if (modalContent) {
                modalContent.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Failed to refresh system status: ${error.message}
                    </div>
                `;
            }
        });
}

function displaySystemStatusModal(data) {
    const modalContent = document.getElementById('system-status-content');
    if (!modalContent) return;
    
    const overallStatus = data.overall_status || 'unknown';
    const statusClass = overallStatus === 'healthy' ? 'success' : 'danger';
    const statusIcon = overallStatus === 'healthy' ? 'check-circle' : 'exclamation-triangle';
    
    let html = `
        <div class="row mb-4">
            <div class="col-12">
                <div class="alert alert-${statusClass}">
                    <h5><i class="fas fa-${statusIcon} me-2"></i>Overall Status: ${overallStatus.toUpperCase()}</h5>
                    <p class="mb-0">Ready for queries: ${data.ready_for_queries ? 'Yes' : 'No'}</p>
                </div>
            </div>
        </div>
    `;
    
    // Vector Store Status
    if (data.vector_store) {
        const vsStatus = data.vector_store.status || 'unknown';
        const vsClass = vsStatus === 'healthy' ? 'success' : 'danger';
        html += `
            <div class="row mb-3">
                <div class="col-12">
                    <h6><i class="fas fa-database me-2"></i>Vector Store</h6>
                    <div class="card">
                        <div class="card-body">
                            <span class="badge bg-${vsClass}">${vsStatus}</span>
                            <p class="mt-2 mb-1"><strong>Document Count:</strong> ${data.vector_store.document_count || 0}</p>
                            ${data.vector_store.embedding_generation ? '<p class="mb-1"><i class="fas fa-check text-success"></i> Embedding Generation: Working</p>' : '<p class="mb-1"><i class="fas fa-times text-danger"></i> Embedding Generation: Failed</p>'}
                            ${data.vector_store.search_functionality ? '<p class="mb-0"><i class="fas fa-check text-success"></i> Search Functionality: Working</p>' : '<p class="mb-0"><i class="fas fa-times text-danger"></i> Search Functionality: Failed</p>'}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    // OpenAI API Status
    html += `
        <div class="row mb-3">
            <div class="col-12">
                <h6><i class="fas fa-robot me-2"></i>OpenAI API</h6>
                <div class="card">
                    <div class="card-body">
                        <span class="badge bg-${data.openai_api === 'healthy' ? 'success' : 'danger'}">${data.openai_api || 'unknown'}</span>
                        <p class="mt-2 mb-0"><strong>Model:</strong> ${data.config?.openai_model || 'Not configured'}</p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Collection Statistics
    if (data.collection_stats) {
        html += `
            <div class="row mb-3">
                <div class="col-12">
                    <h6><i class="fas fa-chart-bar me-2"></i>Collection Statistics</h6>
                    <div class="card">
                        <div class="card-body">
                            <p class="mb-1"><strong>Total Documents:</strong> ${data.collection_stats.total_documents || 0}</p>
                            <p class="mb-1"><strong>Collection:</strong> ${data.collection_stats.collection_name || 'Unknown'}</p>
                            <p class="mb-0"><strong>Sources:</strong> ${data.collection_stats.sources ? data.collection_stats.sources.join(', ') : 'None'}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Timestamp
    html += `
        <div class="row">
            <div class="col-12">
                <small class="text-muted">
                    <i class="fas fa-clock me-1"></i>
                    Last updated: ${data.timestamp ? new Date(data.timestamp).toLocaleString() : 'Unknown'}
                </small>
            </div>
        </div>
    `;
    
    modalContent.innerHTML = html;
    
    // Show modal if not already visible
    const modal = document.getElementById('systemStatusModal');
    if (modal && !modal.classList.contains('show')) {
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }
}

function updateSystemStatusDisplay(data) {
    // Update navigation status indicators
    const statusIndicators = document.querySelectorAll('.chat-status .badge');
    statusIndicators.forEach(indicator => {
        if (data.ready_for_queries) {
            indicator.className = 'badge bg-success';
            indicator.innerHTML = '<i class="fas fa-circle"></i> Ready';
        } else {
            indicator.className = 'badge bg-warning';
            indicator.innerHTML = '<i class="fas fa-hourglass-half"></i> Initializing';
        }
    });
}

function showSystemStatusAlert(message, type = 'info', showSpinner = false) {
    const alert = document.getElementById('system-status-alert');
    if (!alert) return;
    
    const messageElement = document.getElementById('status-message');
    if (messageElement) {
        messageElement.textContent = message;
    }
    
    // Update alert classes
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    
    // Show/hide spinner
    const spinner = alert.querySelector('.spinner-border');
    if (spinner) {
        spinner.style.display = showSpinner ? 'inline-block' : 'none';
    }
    
    alert.classList.remove('d-none');
}

function hideSystemStatusAlert() {
    const alert = document.getElementById('system-status-alert');
    if (alert) {
        alert.classList.add('d-none');
    }
}

// Utility functions
function addLoadingState(button) {
    if (button.dataset.loading === 'true') return;
    
    button.dataset.loading = 'true';
    button.dataset.originalText = button.innerHTML;
    button.disabled = true;
    
    const spinner = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>';
    button.innerHTML = spinner + (button.dataset.loadingText || 'Loading...');
    
    // Auto-restore after 10 seconds as fallback
    setTimeout(() => {
        removeLoadingState(button);
    }, 10000);
}

function removeLoadingState(button) {
    if (button.dataset.loading !== 'true') return;
    
    button.disabled = false;
    button.innerHTML = button.dataset.originalText || button.innerHTML;
    button.dataset.loading = 'false';
    delete button.dataset.originalText;
}

// Form validation helpers
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validateRequired(value) {
    return value && value.trim().length > 0;
}

// Local storage helpers
function setLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
    } catch (error) {
        console.error('Failed to save to localStorage:', error);
        return false;
    }
}

function getLocalStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
        console.error('Failed to read from localStorage:', error);
        return defaultValue;
    }
}

// Error handling
function handleApiError(error, context = 'API call') {
    console.error(`Error in ${context}:`, error);
    
    let message = 'An unexpected error occurred. Please try again.';
    
    if (error.message) {
        message = error.message;
    } else if (typeof error === 'string') {
        message = error;
    }
    
    showAlert(message, 'danger');
}

function showAlert(message, type = 'info', duration = 5000) {
    // Create alert element if it doesn't exist
    let alertContainer = document.getElementById('dynamic-alerts');
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.id = 'dynamic-alerts';
        alertContainer.style.position = 'fixed';
        alertContainer.style.top = '20px';
        alertContainer.style.right = '20px';
        alertContainer.style.zIndex = '9999';
        document.body.appendChild(alertContainer);
    }
    
    const alertId = 'alert-' + Date.now();
    const alertHtml = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show shadow" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('beforeend', alertHtml);
    
    // Auto-dismiss after duration
    if (duration > 0) {
        setTimeout(() => {
            const alertElement = document.getElementById(alertId);
            if (alertElement) {
                alertElement.remove();
            }
        }, duration);
    }
}

// Debounce utility
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle utility
function throttle(func, delay) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, delay);
        }
    };
}

// Copy to clipboard utility
function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            showAlert('Copied to clipboard!', 'success', 2000);
        }).catch(err => {
            console.error('Failed to copy text: ', err);
            showAlert('Failed to copy text', 'danger');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        try {
            document.execCommand('copy');
            showAlert('Copied to clipboard!', 'success', 2000);
        } catch (err) {
            console.error('Failed to copy text: ', err);
            showAlert('Failed to copy text', 'danger');
        }
        document.body.removeChild(textArea);
    }
}

// Format date utility
function formatDate(date, options = {}) {
    const defaultOptions = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    const formatOptions = { ...defaultOptions, ...options };
    return new Date(date).toLocaleDateString('en-US', formatOptions);
}

// Export functions for use in other scripts
window.BNSLegalAssistant = {
    checkSystemStatus,
    refreshSystemStatus,
    showAlert,
    copyToClipboard,
    formatDate,
    debounce,
    throttle,
    addLoadingState,
    removeLoadingState,
    setLocalStorage,
    getLocalStorage,
    handleApiError
};