/**
 * Performance Optimizations for Smart Inventory Management System
 * Client-side performance improvements and UI optimizations
 */

class PerformanceOptimizer {
    constructor() {
        this.debounceTimers = new Map();
        this.lazyLoadObserver = null;
        this.requestCache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
        
        this.init();
    }
    
    init() {
        this.setupLazyLoading();
        this.setupRequestCaching();
        this.setupFormOptimizations();
        this.setupTableOptimizations();
        this.setupImageOptimizations();
        this.monitorPerformance();
    }
    
    /**
     * Debounce function calls to prevent excessive API requests
     */
    debounce(func, delay, key) {
        if (this.debounceTimers.has(key)) {
            clearTimeout(this.debounceTimers.get(key));
        }
        
        const timer = setTimeout(() => {
            func();
            this.debounceTimers.delete(key);
        }, delay);
        
        this.debounceTimers.set(key, timer);
    }
    
    /**
     * Setup lazy loading for images and content
     */
    setupLazyLoading() {
        if ('IntersectionObserver' in window) {
            this.lazyLoadObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const element = entry.target;
                        
                        // Lazy load images
                        if (element.dataset.src) {
                            element.src = element.dataset.src;
                            element.removeAttribute('data-src');
                        }
                        
                        // Lazy load content
                        if (element.dataset.lazyContent) {
                            this.loadLazyContent(element);
                        }
                        
                        this.lazyLoadObserver.unobserve(element);
                    }
                });
            }, {
                rootMargin: '50px 0px',
                threshold: 0.1
            });
            
            // Observe lazy load elements
            document.querySelectorAll('[data-src], [data-lazy-content]').forEach(el => {
                this.lazyLoadObserver.observe(el);
            });
        }
    }
    
    /**
     * Setup request caching to avoid duplicate API calls
     */
    setupRequestCaching() {
        const originalFetch = window.fetch;
        
        window.fetch = (url, options = {}) => {
            // Only cache GET requests
            if (!options.method || options.method.toUpperCase() === 'GET') {
                const cacheKey = url + JSON.stringify(options);
                const cached = this.requestCache.get(cacheKey);
                
                if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
                    return Promise.resolve(cached.response.clone());
                }
                
                return originalFetch(url, options).then(response => {
                    if (response.ok) {
                        this.requestCache.set(cacheKey, {
                            response: response.clone(),
                            timestamp: Date.now()
                        });
                    }
                    return response;
                });
            }
            
            return originalFetch(url, options);
        };
    }
    
    /**
     * Optimize form interactions
     */
    setupFormOptimizations() {
        // Debounced search inputs
        document.querySelectorAll('input[type="search"], .search-input').forEach(input => {
            input.addEventListener('input', (e) => {
                this.debounce(() => {
                    this.handleSearch(e.target);
                }, 300, `search_${e.target.id || e.target.name}`);
            });
        });
        
        // Auto-save form data
        document.querySelectorAll('form[data-autosave]').forEach(form => {
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('change', () => {
                    this.debounce(() => {
                        this.autoSaveForm(form);
                    }, 1000, `autosave_${form.id}`);
                });
            });
        });
        
        // Prevent double form submissions
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
                if (submitBtn && !submitBtn.disabled) {
                    submitBtn.disabled = true;
                    submitBtn.textContent = 'Processing...';
                    
                    // Re-enable after 5 seconds as fallback
                    setTimeout(() => {
                        submitBtn.disabled = false;
                        submitBtn.textContent = submitBtn.dataset.originalText || 'Submit';
                    }, 5000);
                }
            });
        });
    }
    
    /**
     * Optimize table rendering and interactions
     */
    setupTableOptimizations() {
        // Virtual scrolling for large tables
        document.querySelectorAll('table[data-virtual-scroll]').forEach(table => {
            this.setupVirtualScrolling(table);
        });
        
        // Efficient sorting
        document.querySelectorAll('th[data-sortable]').forEach(header => {
            header.addEventListener('click', (e) => {
                this.debounce(() => {
                    this.sortTable(e.target);
                }, 100, `sort_${e.target.dataset.column}`);
            });
        });
        
        // Batch row operations
        document.querySelectorAll('.batch-operations').forEach(container => {
            this.setupBatchOperations(container);
        });
    }
    
    /**
     * Setup image optimizations
     */
    setupImageOptimizations() {
        // Preload critical images
        document.querySelectorAll('img[data-preload]').forEach(img => {
            const preloadImg = new Image();
            preloadImg.src = img.src;
        });
        
        // Progressive image loading
        document.querySelectorAll('img[data-progressive]').forEach(img => {
            this.setupProgressiveLoading(img);
        });
    }
    
    /**
     * Handle search input with debouncing
     */
    handleSearch(input) {
        const searchTerm = input.value.trim();
        const targetUrl = input.dataset.searchUrl;
        
        if (!targetUrl) return;
        
        if (searchTerm.length >= 2) {
            this.performSearch(targetUrl, searchTerm, input);
        } else if (searchTerm.length === 0) {
            this.clearSearchResults(input);
        }
    }
    
    /**
     * Perform search with caching
     */
    async performSearch(url, term, input) {
        try {
            const searchUrl = `${url}?q=${encodeURIComponent(term)}`;
            const response = await fetch(searchUrl);
            
            if (response.ok) {
                const results = await response.json();
                this.displaySearchResults(results, input);
            }
        } catch (error) {
            console.error('Search error:', error);
        }
    }
    
    /**
     * Display search results
     */
    displaySearchResults(results, input) {
        const resultsContainer = document.getElementById(input.dataset.resultsContainer);
        if (!resultsContainer) return;
        
        // Use document fragment for efficient DOM manipulation
        const fragment = document.createDocumentFragment();
        
        results.forEach(result => {
            const resultElement = this.createResultElement(result);
            fragment.appendChild(resultElement);
        });
        
        resultsContainer.innerHTML = '';
        resultsContainer.appendChild(fragment);
    }
    
    /**
     * Auto-save form data to localStorage
     */
    autoSaveForm(form) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        const saveKey = `autosave_${form.id || 'form'}`;
        localStorage.setItem(saveKey, JSON.stringify({
            data: data,
            timestamp: Date.now()
        }));
        
        // Show save indicator
        this.showSaveIndicator(form);
    }
    
    /**
     * Setup virtual scrolling for large tables
     */
    setupVirtualScrolling(table) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        if (rows.length < 100) return; // Only virtualize large tables
        
        const rowHeight = 40; // Approximate row height
        const containerHeight = 400; // Visible container height
        const visibleRows = Math.ceil(containerHeight / rowHeight);
        
        let scrollTop = 0;
        let startIndex = 0;
        
        // Create virtual container
        const virtualContainer = document.createElement('div');
        virtualContainer.style.height = `${rows.length * rowHeight}px`;
        virtualContainer.style.position = 'relative';
        
        const visibleContainer = document.createElement('div');
        visibleContainer.style.height = `${containerHeight}px`;
        visibleContainer.style.overflow = 'auto';
        
        // Replace table body
        tbody.innerHTML = '';
        tbody.appendChild(virtualContainer);
        
        const updateVisibleRows = () => {
            startIndex = Math.floor(scrollTop / rowHeight);
            const endIndex = Math.min(startIndex + visibleRows + 5, rows.length);
            
            // Clear current rows
            virtualContainer.innerHTML = '';
            
            // Add visible rows
            for (let i = startIndex; i < endIndex; i++) {
                const row = rows[i].cloneNode(true);
                row.style.position = 'absolute';
                row.style.top = `${i * rowHeight}px`;
                row.style.width = '100%';
                virtualContainer.appendChild(row);
            }
        };
        
        visibleContainer.addEventListener('scroll', (e) => {
            scrollTop = e.target.scrollTop;
            this.debounce(updateVisibleRows, 16, 'virtual_scroll'); // ~60fps
        });
        
        updateVisibleRows();
    }
    
    /**
     * Setup batch operations for tables
     */
    setupBatchOperations(container) {
        const checkboxes = container.querySelectorAll('input[type="checkbox"]');
        const batchActions = container.querySelectorAll('[data-batch-action]');
        
        // Efficient checkbox selection
        let selectedItems = new Set();
        
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                if (e.target.checked) {
                    selectedItems.add(e.target.value);
                } else {
                    selectedItems.delete(e.target.value);
                }
                
                // Update batch action buttons
                batchActions.forEach(action => {
                    action.disabled = selectedItems.size === 0;
                    action.textContent = `${action.dataset.baseText} (${selectedItems.size})`;
                });
            });
        });
        
        // Select all functionality
        const selectAllCheckbox = container.querySelector('.select-all');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                checkboxes.forEach(checkbox => {
                    checkbox.checked = e.target.checked;
                    if (e.target.checked) {
                        selectedItems.add(checkbox.value);
                    } else {
                        selectedItems.delete(checkbox.value);
                    }
                });
                
                // Update batch actions
                batchActions.forEach(action => {
                    action.disabled = selectedItems.size === 0;
                    action.textContent = `${action.dataset.baseText} (${selectedItems.size})`;
                });
            });
        }
    }
    
    /**
     * Setup progressive image loading
     */
    setupProgressiveLoading(img) {
        const lowResUrl = img.dataset.lowres;
        const highResUrl = img.src;
        
        if (lowResUrl) {
            // Load low-res first
            img.src = lowResUrl;
            img.style.filter = 'blur(2px)';
            
            // Load high-res in background
            const highResImg = new Image();
            highResImg.onload = () => {
                img.src = highResUrl;
                img.style.filter = 'none';
                img.style.transition = 'filter 0.3s ease';
            };
            highResImg.src = highResUrl;
        }
    }
    
    /**
     * Monitor performance metrics
     */
    monitorPerformance() {
        if ('PerformanceObserver' in window) {
            // Monitor long tasks
            const longTaskObserver = new PerformanceObserver((list) => {
                list.getEntries().forEach(entry => {
                    if (entry.duration > 50) { // Tasks longer than 50ms
                        console.warn(`Long task detected: ${entry.duration}ms`);
                    }
                });
            });
            
            try {
                longTaskObserver.observe({ entryTypes: ['longtask'] });
            } catch (e) {
                // Long task API not supported
            }
            
            // Monitor layout shifts
            const layoutShiftObserver = new PerformanceObserver((list) => {
                let cumulativeScore = 0;
                list.getEntries().forEach(entry => {
                    if (!entry.hadRecentInput) {
                        cumulativeScore += entry.value;
                    }
                });
                
                if (cumulativeScore > 0.1) {
                    console.warn(`High cumulative layout shift: ${cumulativeScore}`);
                }
            });
            
            try {
                layoutShiftObserver.observe({ entryTypes: ['layout-shift'] });
            } catch (e) {
                // Layout shift API not supported
            }
        }
        
        // Monitor memory usage
        if ('memory' in performance) {
            setInterval(() => {
                const memInfo = performance.memory;
                const usedMB = memInfo.usedJSHeapSize / 1024 / 1024;
                
                if (usedMB > 50) { // More than 50MB
                    console.warn(`High memory usage: ${usedMB.toFixed(2)}MB`);
                }
            }, 30000); // Check every 30 seconds
        }
    }
    
    /**
     * Utility methods
     */
    createResultElement(result) {
        const div = document.createElement('div');
        div.className = 'search-result-item';
        div.innerHTML = `
            <div class="result-title">${this.escapeHtml(result.title)}</div>
            <div class="result-description">${this.escapeHtml(result.description)}</div>
        `;
        return div;
    }
    
    clearSearchResults(input) {
        const resultsContainer = document.getElementById(input.dataset.resultsContainer);
        if (resultsContainer) {
            resultsContainer.innerHTML = '';
        }
    }
    
    showSaveIndicator(form) {
        let indicator = form.querySelector('.save-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = 'save-indicator';
            indicator.textContent = 'Saved';
            form.appendChild(indicator);
        }
        
        indicator.style.display = 'block';
        indicator.style.opacity = '1';
        
        setTimeout(() => {
            indicator.style.opacity = '0';
            setTimeout(() => {
                indicator.style.display = 'none';
            }, 300);
        }, 2000);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    sortTable(header) {
        const table = header.closest('table');
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const columnIndex = Array.from(header.parentNode.children).indexOf(header);
        const isAscending = !header.classList.contains('sort-asc');
        
        // Remove existing sort classes
        header.parentNode.querySelectorAll('th').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
        });
        
        // Add new sort class
        header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
        
        // Sort rows
        rows.sort((a, b) => {
            const aValue = a.children[columnIndex].textContent.trim();
            const bValue = b.children[columnIndex].textContent.trim();
            
            // Try to parse as numbers
            const aNum = parseFloat(aValue);
            const bNum = parseFloat(bValue);
            
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return isAscending ? aNum - bNum : bNum - aNum;
            }
            
            // String comparison
            return isAscending ? 
                aValue.localeCompare(bValue) : 
                bValue.localeCompare(aValue);
        });
        
        // Re-append sorted rows
        const fragment = document.createDocumentFragment();
        rows.forEach(row => fragment.appendChild(row));
        tbody.appendChild(fragment);
    }
    
    loadLazyContent(element) {
        const contentUrl = element.dataset.lazyContent;
        
        fetch(contentUrl)
            .then(response => response.text())
            .then(html => {
                element.innerHTML = html;
                element.removeAttribute('data-lazy-content');
            })
            .catch(error => {
                console.error('Failed to load lazy content:', error);
                element.innerHTML = '<p>Failed to load content</p>';
            });
    }
}

// Initialize performance optimizer when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.performanceOptimizer = new PerformanceOptimizer();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PerformanceOptimizer;
}