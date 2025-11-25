// SAP Project System Reports Django Application - Enhanced JavaScript Functionality

document.addEventListener('DOMContentLoaded', function() {

    // Initialize all functionality
    initializeAnimations();
    initializeDragAndDrop();
    initializeFormEnhancements();
    initializeTooltips();
    initializeLoadingStates();
    initializeProgressTracking();

    // Fade in animation for page content
    function initializeAnimations() {
        // Add fade-in class to main content
        const mainContent = document.querySelector('main');
        if (mainContent) {
            mainContent.classList.add('fade-in');
        }

        // Stagger animation for cards
        const cards = document.querySelectorAll('.card, .report-card');
        cards.forEach((card, index) => {
            setTimeout(() => {
                card.classList.add('fade-in');
            }, index * 100);
        });

        // Animate navbar on scroll
        let lastScrollTop = 0;
        window.addEventListener('scroll', function() {
            const navbar = document.querySelector('.navbar');
            let scrollTop = window.pageYOffset || document.documentElement.scrollTop;

            // Check if any dropdown is currently open
            const dropdownOpen = document.querySelector('.dropdown-menu.show');

            // Don't hide navbar if dropdown is open or at top of page
            if (dropdownOpen || scrollTop < 100) {
                navbar.style.transform = 'translateY(0)';
                return;
            }

            if (scrollTop > lastScrollTop) {
                // Scrolling down
                navbar.style.transform = 'translateY(-100%)';
            } else {
                // Scrolling up
                navbar.style.transform = 'translateY(0)';
            }
            lastScrollTop = scrollTop;
        });

        // Add dropdown event listeners to manage navbar state
        const dropdowns = document.querySelectorAll('.dropdown');
        dropdowns.forEach(dropdown => {
            const dropdownMenu = dropdown.querySelector('.dropdown-menu');
            const dropdownToggle = dropdown.querySelector('.dropdown-toggle');

            if (dropdownToggle && dropdownMenu) {
                // When dropdown is shown
                dropdownToggle.addEventListener('click', function() {
                    const navbar = document.querySelector('.navbar');
                    navbar.classList.add('dropdown-open');
                });

                // When dropdown is hidden
                document.addEventListener('click', function(event) {
                    if (!dropdown.contains(event.target)) {
                        const navbar = document.querySelector('.navbar');
                        navbar.classList.remove('dropdown-open');
                    }
                });
            }
        });
    }

    // Enhanced Drag and Drop File Upload
    function initializeDragAndDrop() {
        const fileInputs = document.querySelectorAll('input[type="file"]');

        fileInputs.forEach(input => {
            const formGroup = input.closest('.mb-3') || input.parentElement;

            // Get supported formats from accept attribute
            const acceptAttr = input.getAttribute('accept');
            let supportedFormats = '.DAT, .HTML';
            if (acceptAttr) {
                supportedFormats = acceptAttr.split(',').map(ext => ext.trim().toUpperCase()).join(', ');
            }

            // Create enhanced upload area
            const uploadArea = document.createElement('div');
            uploadArea.className = 'file-upload-area';
            uploadArea.innerHTML = `
                <i class="file-upload-icon">📁</i>
                <div class="file-upload-text">Drop your file here or click to browse</div>
                <div class="file-upload-hint">Supported formats: ${supportedFormats}</div>
                <div class="selected-file-name" style="display: none; margin-top: 1rem; color: var(--success-color); font-weight: 600;"></div>
            `;

            // Hide original input and insert upload area
            input.style.display = 'none';
            formGroup.insertBefore(uploadArea, input.nextSibling);

            const selectedFileName = uploadArea.querySelector('.selected-file-name');

            // Click to browse
            uploadArea.addEventListener('click', () => {
                input.click();
            });

            // File selection change
            input.addEventListener('change', function() {
                if (this.files && this.files.length > 0) {
                    const fileName = this.files[0].name;
                    selectedFileName.textContent = `Selected: ${fileName}`;
                    selectedFileName.style.display = 'block';
                    uploadArea.classList.add('file-selected');
                }
            });

            // Drag and drop functionality
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                uploadArea.addEventListener(eventName, preventDefaults, false);
            });

            function preventDefaults(e) {
                e.preventDefault();
                e.stopPropagation();
            }

            ['dragenter', 'dragover'].forEach(eventName => {
                uploadArea.addEventListener(eventName, () => {
                    uploadArea.classList.add('drag-over');
                }, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                uploadArea.addEventListener(eventName, () => {
                    uploadArea.classList.remove('drag-over');
                }, false);
            });

            uploadArea.addEventListener('drop', function(e) {
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    input.files = files;
                    const fileName = files[0].name;
                    selectedFileName.textContent = `Selected: ${fileName}`;
                    selectedFileName.style.display = 'block';
                    uploadArea.classList.add('file-selected');
                }
            });
        });
    }

    // Form Enhancement with Loading States
    function initializeFormEnhancements() {
        const forms = document.querySelectorAll('form[method="post"]');

        forms.forEach(form => {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (!submitBtn) return;

            const originalText = submitBtn.textContent;
            const loadingText = getLoadingText(originalText);

            form.addEventListener('submit', function(e) {
                // Show loading state
                submitBtn.disabled = true;
                submitBtn.innerHTML = `<span class="loading-spinner"></span>${loadingText}`;

                // Add progress bar
                showProgressBar();

                // Validate file input if present
                const fileInput = form.querySelector('input[type="file"]');
                if (fileInput && (!fileInput.files || fileInput.files.length === 0)) {
                    e.preventDefault();
                    showAlert('Please select a file before submitting.', 'danger');
                    resetSubmitButton();
                    return;
                }

                // Validate file type based on accept attribute
                if (fileInput && fileInput.files.length > 0) {
                    const file = fileInput.files[0];
                    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));

                    // Get allowed extensions from the accept attribute
                    const acceptAttr = fileInput.getAttribute('accept');
                    if (acceptAttr) {
                        const allowedExtensions = acceptAttr.split(',').map(ext => ext.trim());

                        if (!allowedExtensions.includes(fileExtension)) {
                            e.preventDefault();
                            const formatList = allowedExtensions.join(', ').toUpperCase();
                            showAlert(`Please select a valid file (${formatList})`, 'danger');
                            resetSubmitButton();
                            return;
                        }
                    }
                }

                // Show estimated processing time
                showProcessingEstimate();
            });

            function resetSubmitButton() {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
                hideProgressBar();
            }

            function getLoadingText(original) {
                if (original.toLowerCase().includes('generate')) return 'Generating Report...';
                if (original.toLowerCase().includes('upload')) return 'Uploading...';
                if (original.toLowerCase().includes('submit')) return 'Processing...';
                return 'Please wait...';
            }
        });
    }

    // Progress Bar Management
    function showProgressBar() {
        const existingProgress = document.querySelector('.upload-progress');
        if (existingProgress) return;

        const progressContainer = document.createElement('div');
        progressContainer.className = 'upload-progress mt-3';
        progressContainer.innerHTML = `
            <div class="progress">
                <div class="progress-bar" role="progressbar" style="width: 0%"></div>
            </div>
            <div class="progress-text text-center mt-2">
                <small class="text-muted">Processing your file...</small>
            </div>
        `;

        const form = document.querySelector('form[method="post"]');
        if (form) {
            form.appendChild(progressContainer);

            // Simulate progress
            const progressBar = progressContainer.querySelector('.progress-bar');
            const progressText = progressContainer.querySelector('.progress-text small');

            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress > 90) progress = 90;

                progressBar.style.width = progress + '%';

                if (progress < 30) {
                    progressText.textContent = 'Validating file format...';
                } else if (progress < 60) {
                    progressText.textContent = 'Processing SAP data...';
                } else if (progress < 90) {
                    progressText.textContent = 'Generating Excel report...';
                }

                if (progress >= 90) {
                    clearInterval(interval);
                    progressText.textContent = 'Finalizing report...';
                }
            }, 200);
        }
    }

    function hideProgressBar() {
        const progressContainer = document.querySelector('.upload-progress');
        if (progressContainer) {
            progressContainer.remove();
        }
    }

    function showProcessingEstimate() {
        const estimate = document.createElement('div');
        estimate.className = 'alert alert-info mt-3 processing-estimate fade-in';
        estimate.innerHTML = `
            <strong>Processing Time:</strong> Large files may take 30-60 seconds to process.
            Please do not close this window.
        `;

        const form = document.querySelector('form[method="post"]');
        if (form) {
            form.appendChild(estimate);
        }
    }

    // Initialize Bootstrap Tooltips
    function initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Loading States for Navigation
    function initializeLoadingStates() {
        const navLinks = document.querySelectorAll('.nav-link, .report-button, .list-group-item-action');

        navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                if (this.href && !this.href.includes('#')) {
                    const loadingOverlay = showLoadingOverlay('Loading page...');

                    // Remove loading overlay if page doesn't change within 5 seconds
                    setTimeout(() => {
                        if (loadingOverlay && loadingOverlay.parentNode) {
                            loadingOverlay.remove();
                        }
                    }, 5000);
                }
            });
        });
    }

    function showLoadingOverlay(message = 'Loading...') {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(5px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            flex-direction: column;
        `;

        overlay.innerHTML = `
            <div class="loading-spinner" style="width: 40px; height: 40px; border-width: 4px; margin-bottom: 1rem;"></div>
            <div style="font-size: 1.1rem; color: var(--dark-color);">${message}</div>
        `;

        document.body.appendChild(overlay);
        return overlay;
    }

    // Alert System
    function showAlert(message, type = 'info', duration = 5000) {
        const alertContainer = document.querySelector('.alert-container') || createAlertContainer();

        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        alertContainer.appendChild(alert);

        // Auto-dismiss
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, duration);

        return alert;
    }

    function createAlertContainer() {
        const container = document.createElement('div');
        container.className = 'alert-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1050;
            max-width: 400px;
        `;
        document.body.appendChild(container);
        return container;
    }

    // Progress Tracking for File Operations
    function initializeProgressTracking() {
        // Track download progress
        const downloadLinks = document.querySelectorAll('a[href*="download"]');
        downloadLinks.forEach(link => {
            link.addEventListener('click', function() {
                showAlert('Download started! Check your downloads folder.', 'success');
            });
        });

        // Auto-refresh for report status
        if (window.location.pathname.includes('report')) {
            const refreshInterval = 30000; // 30 seconds
            setTimeout(() => {
                const alerts = document.querySelectorAll('.alert-success, .alert-danger');
                if (alerts.length === 0) {
                    // No success or error alerts, might still be processing
                    showAlert('Still processing... Please wait.', 'info');
                }
            }, refreshInterval);
        }
    }

    // Enhanced Table Functionality
    function initializeTableEnhancements() {
        const tables = document.querySelectorAll('.table-responsive table');
        tables.forEach(table => {
            // Add sorting functionality
            const headers = table.querySelectorAll('th');
            headers.forEach((header, index) => {
                header.style.cursor = 'pointer';
                header.title = 'Click to sort';

                header.addEventListener('click', () => {
                    sortTable(table, index);
                });
            });
        });
    }

    function sortTable(table, columnIndex) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));

        const isNumeric = rows.every(row => {
            const cellText = row.cells[columnIndex]?.textContent.trim();
            return !isNaN(cellText) && cellText !== '';
        });

        rows.sort((a, b) => {
            const aText = a.cells[columnIndex]?.textContent.trim() || '';
            const bText = b.cells[columnIndex]?.textContent.trim() || '';

            if (isNumeric) {
                return parseFloat(aText) - parseFloat(bText);
            } else {
                return aText.localeCompare(bText);
            }
        });

        rows.forEach(row => tbody.appendChild(row));
    }

    // Initialize table enhancements if tables exist
    if (document.querySelector('.table-responsive table')) {
        initializeTableEnhancements();
    }

    // Keyboard Shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl + Enter to submit forms
        if (e.ctrlKey && e.key === 'Enter') {
            const form = document.querySelector('form[method="post"]');
            if (form) {
                form.submit();
            }
        }

        // Escape to go back
        if (e.key === 'Escape') {
            const backButton = document.querySelector('a[href*="dashboard"]');
            if (backButton) {
                window.location.href = backButton.href;
            }
        }
    });

    // Performance monitoring
    if ('performance' in window) {
        window.addEventListener('load', function() {
            setTimeout(() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                if (perfData && perfData.loadEventEnd - perfData.loadEventStart > 3000) {
                    console.log('Slow page load detected:', Math.round(perfData.loadEventEnd - perfData.loadEventStart) + 'ms');
                }
            }, 0);
        });
    }

});

// Utility functions available globally
window.SAPReports = {
    showAlert: function(message, type = 'info', duration = 5000) {
        // Reuse the showAlert function from above
        const alertContainer = document.querySelector('.alert-container') || createAlertContainer();

        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        alertContainer.appendChild(alert);

        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, duration);

        return alert;
    },

    showLoading: function(message = 'Loading...') {
        return showLoadingOverlay(message);
    },

    hideLoading: function(overlay) {
        if (overlay && overlay.parentNode) {
            overlay.remove();
        }
    }
};

// Helper function for alert container creation (moved to global scope)
function createAlertContainer() {
    const container = document.createElement('div');
    container.className = 'alert-container';
    container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1050;
        max-width: 400px;
    `;
    document.body.appendChild(container);
    return container;
}

function showLoadingOverlay(message = 'Loading...') {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(5px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        flex-direction: column;
    `;

    overlay.innerHTML = `
        <div class="loading-spinner" style="width: 40px; height: 40px; border-width: 4px; margin-bottom: 1rem;"></div>
        <div style="font-size: 1.1rem; color: var(--dark-color);">${message}</div>
    `;

    document.body.appendChild(overlay);
    return overlay;
}