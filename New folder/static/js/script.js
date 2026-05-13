// Smart Inventory Management System - JavaScript Functions

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Add fade-in animation to cards
    $('.card').addClass('fade-in');

    // Form validation enhancements
    $('form').on('submit', function() {
        $(this).find('button[type="submit"]').prop('disabled', true).html('<span class="loading-spinner"></span> Processing...');
    });

    // Quick purchase request functionality
    $('.quick-purchase-form').on('submit', function(e) {
        e.preventDefault();
        
        var form = $(this);
        var productId = form.find('input[name="product_id"]').val();
        var quantity = form.find('input[name="quantity"]').val();
        var button = form.find('button[type="submit"]');
        
        // Disable button and show loading
        button.prop('disabled', true).html('<span class="loading-spinner"></span> Submitting...');
        
        $.ajax({
            url: '/api/products/' + productId + '/quick-request',
            method: 'POST',
            data: {
                quantity: quantity
            },
            success: function(response) {
                if (response.success) {
                    showAlert('success', response.message);
                    form[0].reset();
                } else {
                    showAlert('error', response.error || 'An error occurred');
                }
            },
            error: function(xhr) {
                var errorMsg = 'An error occurred';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMsg = xhr.responseJSON.error;
                }
                showAlert('error', errorMsg);
            },
            complete: function() {
                button.prop('disabled', false).html('<i class="fas fa-shopping-cart"></i> Request');
            }
        });
    });

    // Quick process request functionality
    $('.quick-process-form').on('submit', function(e) {
        e.preventDefault();
        
        var form = $(this);
        var requestId = form.find('input[name="request_id"]').val();
        var action = form.find('select[name="action"]').val();
        var reason = form.find('textarea[name="reason"]').val();
        var button = form.find('button[type="submit"]');
        
        if (action === 'reject' && !reason.trim()) {
            showAlert('error', 'Rejection reason is required');
            return;
        }
        
        // Disable button and show loading
        button.prop('disabled', true).html('<span class="loading-spinner"></span> Processing...');
        
        $.ajax({
            url: '/api/admin/purchase-requests/' + requestId + '/quick-process',
            method: 'POST',
            data: {
                action: action,
                reason: reason
            },
            success: function(response) {
                if (response.success) {
                    showAlert('success', response.message);
                    
                    // Update the row status
                    var row = form.closest('tr');
                    var statusBadge = row.find('.status-badge');
                    statusBadge.removeClass('status-pending status-approved status-rejected')
                           .addClass('status-' + response.new_status)
                           .text(response.new_status.charAt(0).toUpperCase() + response.new_status.slice(1));
                    
                    // Hide the form
                    form.hide();
                } else {
                    showAlert('error', response.error || 'An error occurred');
                }
            },
            error: function(xhr) {
                var errorMsg = 'An error occurred';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMsg = xhr.responseJSON.error;
                }
                showAlert('error', errorMsg);
            },
            complete: function() {
                button.prop('disabled', false).html('Process');
            }
        });
    });

    // Bulk selection functionality
    $('#select-all').on('change', function() {
        $('.request-checkbox').prop('checked', $(this).prop('checked'));
        updateBulkActionButton();
    });

    $('.request-checkbox').on('change', function() {
        updateBulkActionButton();
        
        // Update select-all checkbox
        var totalCheckboxes = $('.request-checkbox').length;
        var checkedCheckboxes = $('.request-checkbox:checked').length;
        
        $('#select-all').prop('indeterminate', checkedCheckboxes > 0 && checkedCheckboxes < totalCheckboxes);
        $('#select-all').prop('checked', checkedCheckboxes === totalCheckboxes);
    });

    // Product search functionality
    $('#product-search').on('input', function() {
        var searchTerm = $(this).val().toLowerCase();
        
        $('.product-card').each(function() {
            var productName = $(this).find('.card-title').text().toLowerCase();
            var productCategory = $(this).find('.product-category').text().toLowerCase();
            
            if (productName.includes(searchTerm) || productCategory.includes(searchTerm)) {
                $(this).closest('.col-md-4').show();
            } else {
                $(this).closest('.col-md-4').hide();
            }
        });
    });

    // Category filter functionality
    $('#category-filter').on('change', function() {
        var selectedCategory = $(this).val();
        
        $('.product-card').each(function() {
            var productCategory = $(this).find('.product-category').text();
            
            if (selectedCategory === '' || productCategory === selectedCategory) {
                $(this).closest('.col-md-4').show();
            } else {
                $(this).closest('.col-md-4').hide();
            }
        });
    });

    // Confirmation dialogs
    $('.confirm-action').on('click', function(e) {
        var message = $(this).data('confirm') || 'Are you sure you want to perform this action?';
        if (!confirm(message)) {
            e.preventDefault();
        }
    });

    // Number input validation
    $('input[type="number"]').on('input', function() {
        var min = parseInt($(this).attr('min'));
        var max = parseInt($(this).attr('max'));
        var value = parseInt($(this).val());
        
        if (value < min) {
            $(this).val(min);
        } else if (value > max) {
            $(this).val(max);
        }
    });

    // Auto-refresh functionality for dashboard
    if ($('#dashboard-stats').length > 0) {
        setInterval(function() {
            refreshDashboardStats();
        }, 30000); // Refresh every 30 seconds
    }
});

// Utility Functions

function showAlert(type, message) {
    var alertClass = type === 'error' ? 'danger' : type;
    var iconClass = getAlertIcon(type);
    
    var alertHtml = `
        <div class="alert alert-${alertClass} alert-dismissible fade show" role="alert">
            <i class="${iconClass}"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    $('.container').first().prepend(alertHtml);
    
    // Auto-hide after 5 seconds
    setTimeout(function() {
        $('.alert').first().fadeOut('slow');
    }, 5000);
}

function getAlertIcon(type) {
    switch(type) {
        case 'success': return 'fas fa-check-circle';
        case 'error': return 'fas fa-exclamation-triangle';
        case 'warning': return 'fas fa-exclamation-circle';
        case 'info': return 'fas fa-info-circle';
        default: return 'fas fa-info-circle';
    }
}

function updateBulkActionButton() {
    var checkedCount = $('.request-checkbox:checked').length;
    var bulkButton = $('#bulk-action-button');
    
    if (checkedCount > 0) {
        bulkButton.prop('disabled', false).text(`Process ${checkedCount} Selected`);
    } else {
        bulkButton.prop('disabled', true).text('Select Requests');
    }
}

function refreshDashboardStats() {
    $.ajax({
        url: '/api/admin/dashboard/stats',
        method: 'GET',
        success: function(data) {
            // Update dashboard statistics
            $('#total-products').text(data.total_products || 0);
            $('#low-stock-count').text(data.low_stock_count || 0);
            $('#pending-requests').text(data.pending_requests || 0);
            $('#total-sales').text('$' + (data.total_sales || 0).toFixed(2));
        },
        error: function() {
            console.log('Failed to refresh dashboard stats');
        }
    });
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Form validation helpers
function validateEmail(email) {
    var re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePassword(password) {
    // At least 8 characters, 1 uppercase, 1 lowercase, 1 number, 1 special char
    var re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    return re.test(password);
}

// Advanced Features

// Notification System
class NotificationSystem {
    constructor() {
        this.notifications = [];
        this.container = null;
        this.init();
    }
    
    init() {
        // Create notification container if it doesn't exist
        if (!document.getElementById('notification-container')) {
            this.container = document.createElement('div');
            this.container.id = 'notification-container';
            this.container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 400px;
            `;
            document.body.appendChild(this.container);
        } else {
            this.container = document.getElementById('notification-container');
        }
    }
    
    show(type, title, message, duration = 5000) {
        const notification = document.createElement('div');
        const id = 'notification-' + Date.now();
        notification.id = id;
        
        const iconMap = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-triangle',
            warning: 'fas fa-exclamation-circle',
            info: 'fas fa-info-circle'
        };
        
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show mb-2`;
        notification.style.cssText = `
            animation: slideInRight 0.3s ease-out;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        
        notification.innerHTML = `
            <div class="d-flex align-items-start">
                <i class="${iconMap[type]} me-2 mt-1"></i>
                <div class="flex-grow-1">
                    <strong>${title}</strong>
                    <div>${message}</div>
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        this.container.appendChild(notification);
        
        // Auto-remove after duration
        if (duration > 0) {
            setTimeout(() => {
                this.remove(id);
            }, duration);
        }
        
        return id;
    }
    
    remove(id) {
        const notification = document.getElementById(id);
        if (notification) {
            notification.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }
    }
}

// Initialize notification system
const notifications = new NotificationSystem();

// Enhanced Form Validation
class FormValidator {
    constructor(form) {
        this.form = form;
        this.rules = {};
        this.init();
    }
    
    init() {
        this.form.addEventListener('submit', (e) => {
            if (!this.validate()) {
                e.preventDefault();
            }
        });
        
        // Real-time validation
        this.form.querySelectorAll('input, select, textarea').forEach(field => {
            field.addEventListener('blur', () => {
                this.validateField(field);
            });
            
            field.addEventListener('input', () => {
                this.clearFieldError(field);
            });
        });
    }
    
    addRule(fieldName, validator, message) {
        if (!this.rules[fieldName]) {
            this.rules[fieldName] = [];
        }
        this.rules[fieldName].push({ validator, message });
    }
    
    validate() {
        let isValid = true;
        
        Object.keys(this.rules).forEach(fieldName => {
            const field = this.form.querySelector(`[name="${fieldName}"]`);
            if (field && !this.validateField(field)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    validateField(field) {
        const fieldName = field.name;
        const rules = this.rules[fieldName] || [];
        
        this.clearFieldError(field);
        
        for (let rule of rules) {
            if (!rule.validator(field.value, field)) {
                this.showFieldError(field, rule.message);
                return false;
            }
        }
        
        this.showFieldSuccess(field);
        return true;
    }
    
    showFieldError(field, message) {
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');
        
        let feedback = field.parentNode.querySelector('.invalid-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            field.parentNode.appendChild(feedback);
        }
        feedback.textContent = message;
    }
    
    showFieldSuccess(field) {
        field.classList.add('is-valid');
        field.classList.remove('is-invalid');
    }
    
    clearFieldError(field) {
        field.classList.remove('is-invalid', 'is-valid');
        const feedback = field.parentNode.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.remove();
        }
    }
}

// Data Table Enhancement
class DataTable {
    constructor(tableElement, options = {}) {
        this.table = tableElement;
        this.options = {
            sortable: true,
            filterable: true,
            paginated: true,
            pageSize: 10,
            ...options
        };
        this.currentPage = 1;
        this.sortColumn = null;
        this.sortDirection = 'asc';
        this.filterText = '';
        this.init();
    }
    
    init() {
        if (this.options.sortable) {
            this.initSorting();
        }
        
        if (this.options.filterable) {
            this.initFiltering();
        }
        
        if (this.options.paginated) {
            this.initPagination();
        }
    }
    
    initSorting() {
        const headers = this.table.querySelectorAll('thead th');
        headers.forEach((header, index) => {
            if (header.dataset.sortable !== 'false') {
                header.style.cursor = 'pointer';
                header.addEventListener('click', () => {
                    this.sort(index);
                });
            }
        });
    }
    
    sort(columnIndex) {
        const rows = Array.from(this.table.querySelectorAll('tbody tr'));
        
        if (this.sortColumn === columnIndex) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortColumn = columnIndex;
            this.sortDirection = 'asc';
        }
        
        rows.sort((a, b) => {
            const aValue = a.cells[columnIndex].textContent.trim();
            const bValue = b.cells[columnIndex].textContent.trim();
            
            let comparison = 0;
            if (aValue > bValue) comparison = 1;
            if (aValue < bValue) comparison = -1;
            
            return this.sortDirection === 'asc' ? comparison : -comparison;
        });
        
        const tbody = this.table.querySelector('tbody');
        rows.forEach(row => tbody.appendChild(row));
        
        this.updateSortIndicators();
    }
    
    updateSortIndicators() {
        const headers = this.table.querySelectorAll('thead th');
        headers.forEach((header, index) => {
            const icon = header.querySelector('.sort-icon');
            if (icon) icon.remove();
            
            if (index === this.sortColumn) {
                const sortIcon = document.createElement('i');
                sortIcon.className = `fas fa-sort-${this.sortDirection === 'asc' ? 'up' : 'down'} sort-icon ms-1`;
                header.appendChild(sortIcon);
            }
        });
    }
}

// Real-time Search
class LiveSearch {
    constructor(searchInput, targetSelector, options = {}) {
        this.searchInput = searchInput;
        this.targets = document.querySelectorAll(targetSelector);
        this.options = {
            delay: 300,
            minLength: 2,
            highlightMatches: true,
            ...options
        };
        this.timeout = null;
        this.init();
    }
    
    init() {
        this.searchInput.addEventListener('input', (e) => {
            clearTimeout(this.timeout);
            this.timeout = setTimeout(() => {
                this.search(e.target.value);
            }, this.options.delay);
        });
    }
    
    search(query) {
        const searchTerm = query.toLowerCase().trim();
        
        if (searchTerm.length < this.options.minLength && searchTerm.length > 0) {
            return;
        }
        
        this.targets.forEach(target => {
            const text = target.textContent.toLowerCase();
            const matches = searchTerm === '' || text.includes(searchTerm);
            
            if (matches) {
                target.style.display = '';
                if (this.options.highlightMatches && searchTerm) {
                    this.highlightText(target, searchTerm);
                }
            } else {
                target.style.display = 'none';
            }
        });
    }
    
    highlightText(element, searchTerm) {
        // Simple text highlighting implementation
        const walker = document.createTreeWalker(
            element,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        const textNodes = [];
        let node;
        
        while (node = walker.nextNode()) {
            textNodes.push(node);
        }
        
        textNodes.forEach(textNode => {
            const text = textNode.textContent;
            const regex = new RegExp(`(${searchTerm})`, 'gi');
            
            if (regex.test(text)) {
                const highlightedText = text.replace(regex, '<mark>$1</mark>');
                const wrapper = document.createElement('span');
                wrapper.innerHTML = highlightedText;
                textNode.parentNode.replaceChild(wrapper, textNode);
            }
        });
    }
}

// Auto-save functionality
class AutoSave {
    constructor(form, options = {}) {
        this.form = form;
        this.options = {
            interval: 30000, // 30 seconds
            endpoint: '/api/autosave',
            key: 'autosave_' + (form.id || 'form'),
            ...options
        };
        this.timeout = null;
        this.init();
    }
    
    init() {
        // Load saved data
        this.loadSavedData();
        
        // Set up auto-save
        this.form.addEventListener('input', () => {
            clearTimeout(this.timeout);
            this.timeout = setTimeout(() => {
                this.save();
            }, this.options.interval);
        });
        
        // Save on form submit
        this.form.addEventListener('submit', () => {
            this.clearSavedData();
        });
    }
    
    save() {
        const formData = new FormData(this.form);
        const data = Object.fromEntries(formData.entries());
        
        // Save to localStorage
        localStorage.setItem(this.options.key, JSON.stringify(data));
        
        // Optionally save to server
        if (this.options.endpoint) {
            fetch(this.options.endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            }).catch(error => {
                console.log('Auto-save failed:', error);
            });
        }
    }
    
    loadSavedData() {
        const savedData = localStorage.getItem(this.options.key);
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                Object.keys(data).forEach(key => {
                    const field = this.form.querySelector(`[name="${key}"]`);
                    if (field) {
                        field.value = data[key];
                    }
                });
                
                notifications.show('info', 'Draft Restored', 'Your previous work has been restored.');
            } catch (error) {
                console.log('Failed to load saved data:', error);
            }
        }
    }
    
    clearSavedData() {
        localStorage.removeItem(this.options.key);
    }
}

// Enhanced utility functions
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func(...args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        return navigator.clipboard.writeText(text);
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        return Promise.resolve();
    }
}

// Enhanced showAlert function
function showAlert(type, message, title = null) {
    if (title) {
        notifications.show(type, title, message);
    } else {
        notifications.show(type, type.charAt(0).toUpperCase() + type.slice(1), message);
    }
}

// Export enhanced functions for use in other scripts
window.InventorySystem = {
    showAlert: showAlert,
    formatCurrency: formatCurrency,
    formatDate: formatDate,
    validateEmail: validateEmail,
    validatePassword: validatePassword,
    NotificationSystem: NotificationSystem,
    FormValidator: FormValidator,
    DataTable: DataTable,
    LiveSearch: LiveSearch,
    AutoSave: AutoSave,
    debounce: debounce,
    throttle: throttle,
    copyToClipboard: copyToClipboard,
    notifications: notifications
};
// In
itialize enhanced features when DOM is loaded
$(document).ready(function() {
    // Initialize enhanced data tables
    $('.data-table').each(function() {
        new DataTable(this);
    });
    
    // Initialize live search
    const searchInputs = document.querySelectorAll('[data-live-search]');
    searchInputs.forEach(input => {
        const target = input.dataset.liveSearch;
        new LiveSearch(input, target);
    });
    
    // Initialize form validators
    $('form[data-validate]').each(function() {
        const validator = new FormValidator(this);
        
        // Add common validation rules
        validator.addRule('email', (value) => validateEmail(value), 'Please enter a valid email address');
        validator.addRule('password', (value) => validatePassword(value), 'Password must be at least 8 characters with uppercase, lowercase, number, and special character');
        validator.addRule('required', (value) => value.trim() !== '', 'This field is required');
    });
    
    // Initialize auto-save for forms
    $('form[data-autosave]').each(function() {
        new AutoSave(this);
    });
    
    // Enhanced button interactions
    $('.btn').on('click', function() {
        if (!$(this).hasClass('btn-loading')) {
            $(this).addClass('btn-clicked');
            setTimeout(() => {
                $(this).removeClass('btn-clicked');
            }, 200);
        }
    });
    
    // Smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(event) {
        const target = $(this.getAttribute('href'));
        if (target.length) {
            event.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 100
            }, 1000, 'easeInOutExpo');
        }
    });
    
    // Lazy loading for images
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
    
    // Enhanced modal interactions
    $('.modal').on('show.bs.modal', function() {
        $(this).find('.modal-dialog').addClass('modal-show');
    });
    
    $('.modal').on('hide.bs.modal', function() {
        $(this).find('.modal-dialog').removeClass('modal-show');
    });
    
    // Keyboard shortcuts
    $(document).on('keydown', function(e) {
        // Ctrl/Cmd + S to save forms
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            const activeForm = document.activeElement.closest('form');
            if (activeForm) {
                $(activeForm).submit();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            $('.modal.show').modal('hide');
        }
    });
    
    // Enhanced tooltips with delay
    $('[data-bs-toggle="tooltip"]').tooltip({
        delay: { show: 500, hide: 100 }
    });
    
    // Progress indicators for long operations
    window.showProgress = function(message = 'Processing...') {
        const progressHtml = `
            <div id="progress-overlay" class="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center" style="background: rgba(0,0,0,0.5); z-index: 9999;">
                <div class="bg-white p-4 rounded shadow text-center">
                    <div class="spinner-border text-primary mb-3" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <div>${message}</div>
                </div>
            </div>
        `;
        $('body').append(progressHtml);
    };
    
    window.hideProgress = function() {
        $('#progress-overlay').fadeOut(300, function() {
            $(this).remove();
        });
    };
    
    // Enhanced form submission with progress
    $('form[data-progress]').on('submit', function() {
        const message = $(this).data('progress') || 'Processing your request...';
        showProgress(message);
    });
    
    // Auto-refresh functionality
    $('[data-auto-refresh]').each(function() {
        const element = $(this);
        const interval = parseInt(element.data('auto-refresh')) * 1000;
        const url = element.data('refresh-url') || window.location.href;
        
        setInterval(function() {
            $.get(url).done(function(data) {
                const newContent = $(data).find('#' + element.attr('id')).html();
                if (newContent) {
                    element.html(newContent);
                }
            });
        }, interval);
    });
    
    // Enhanced copy to clipboard functionality
    $('[data-copy]').on('click', function() {
        const text = $(this).data('copy');
        copyToClipboard(text).then(() => {
            notifications.show('success', 'Copied!', 'Text copied to clipboard');
        }).catch(() => {
            notifications.show('error', 'Failed', 'Could not copy to clipboard');
        });
    });
    
    // Print functionality
    $('[data-print]').on('click', function() {
        const target = $(this).data('print');
        if (target) {
            const printContent = $(target).html();
            const printWindow = window.open('', '_blank');
            printWindow.document.write(`
                <html>
                    <head>
                        <title>Print</title>
                        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                        <style>
                            body { padding: 20px; }
                            @media print { .no-print { display: none !important; } }
                        </style>
                    </head>
                    <body>
                        ${printContent}
                        <script>window.print(); window.close();</script>
                    </body>
                </html>
            `);
            printWindow.document.close();
        }
    });
    
    // Enhanced table row selection
    $('.table-selectable tbody tr').on('click', function() {
        $(this).toggleClass('table-active');
        const checkbox = $(this).find('input[type="checkbox"]');
        if (checkbox.length) {
            checkbox.prop('checked', !checkbox.prop('checked'));
        }
    });
    
    // Bulk actions for tables
    $('.select-all').on('change', function() {
        const table = $(this).closest('table');
        const checkboxes = table.find('tbody input[type="checkbox"]');
        checkboxes.prop('checked', $(this).prop('checked'));
        updateBulkActions(table);
    });
    
    $('.table tbody input[type="checkbox"]').on('change', function() {
        const table = $(this).closest('table');
        updateBulkActions(table);
    });
    
    function updateBulkActions(table) {
        const checkboxes = table.find('tbody input[type="checkbox"]');
        const checkedCount = checkboxes.filter(':checked').length;
        const bulkActions = table.closest('.table-container').find('.bulk-actions');
        
        if (checkedCount > 0) {
            bulkActions.removeClass('d-none');
            bulkActions.find('.selected-count').text(checkedCount);
        } else {
            bulkActions.addClass('d-none');
        }
    }
    
    // Enhanced file upload with drag and drop
    $('.file-drop-zone').on('dragover', function(e) {
        e.preventDefault();
        $(this).addClass('drag-over');
    });
    
    $('.file-drop-zone').on('dragleave', function(e) {
        e.preventDefault();
        $(this).removeClass('drag-over');
    });
    
    $('.file-drop-zone').on('drop', function(e) {
        e.preventDefault();
        $(this).removeClass('drag-over');
        
        const files = e.originalEvent.dataTransfer.files;
        const input = $(this).find('input[type="file"]')[0];
        if (input && files.length > 0) {
            input.files = files;
            $(input).trigger('change');
        }
    });
    
    // Enhanced number inputs with increment/decrement
    $('.number-input-group').each(function() {
        const input = $(this).find('input[type="number"]');
        const decrementBtn = $(this).find('.btn-decrement');
        const incrementBtn = $(this).find('.btn-increment');
        
        decrementBtn.on('click', function() {
            const currentValue = parseInt(input.val()) || 0;
            const min = parseInt(input.attr('min')) || 0;
            if (currentValue > min) {
                input.val(currentValue - 1).trigger('change');
            }
        });
        
        incrementBtn.on('click', function() {
            const currentValue = parseInt(input.val()) || 0;
            const max = parseInt(input.attr('max')) || Infinity;
            if (currentValue < max) {
                input.val(currentValue + 1).trigger('change');
            }
        });
    });
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    .btn-clicked {
        animation: pulse 0.2s ease-in-out;
    }
    
    .modal-show {
        animation: slideInUp 0.3s ease-out;
    }
    
    @keyframes slideInUp {
        from { transform: translateY(50px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .drag-over {
        border-color: var(--primary-color) !important;
        background-color: rgba(0, 123, 255, 0.1) !important;
    }
    
    .table-active {
        background-color: rgba(0, 123, 255, 0.1) !important;
    }
    
    .lazy {
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .lazy.loaded {
        opacity: 1;
    }
`;
document.head.appendChild(style);