// ===========================
// app/static/js/main.js
// ===========================

class WebScraperApp {
    constructor() {
        this.scrapedData = {};
        this.apiBaseUrl = '/api';
        this.isLoading = false;
        this.initializeEventListeners();
        this.initializeAnimations();
    }

    initializeEventListeners() {
        // Form submission
        const form = document.getElementById('scrapeForm');
        if (form) {
            form.addEventListener('submit', (e) => this.handleScrapeSubmit(e));
        }

        // Download button
        const downloadBtn = document.getElementById('downloadBtn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => this.handleDownload());
        }

        // Copy button
        const copyBtn = document.getElementById('copyBtn');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => this.handleCopy());
        }

        // JSON formatting controls
        const formatBtn = document.getElementById('formatBtn');
        const collapseBtn = document.getElementById('collapseBtn');
        
        if (formatBtn) {
            formatBtn.addEventListener('click', () => this.formatJSON());
        }
        
        if (collapseBtn) {
            collapseBtn.addEventListener('click', () => this.collapseJSON());
        }

        // Real-time URL validation
        const urlInput = document.getElementById('url');
        if (urlInput) {
            urlInput.addEventListener('input', (e) => this.validateURL(e.target.value));
        }

        // Option card interactions
        this.initializeOptionCards();
    }

    initializeAnimations() {
        // Intersection Observer for scroll animations
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, { threshold: 0.1 });

        // Observe stat cards for animation
        document.addEventListener('DOMContentLoaded', () => {
            const statCards = document.querySelectorAll('.stat-card');
            statCards.forEach(card => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                card.style.transition = 'all 0.6s ease';
                observer.observe(card);
            });
        });
    }

    initializeOptionCards() {
        const optionCards = document.querySelectorAll('.option-card');
        optionCards.forEach(card => {
            const checkbox = card.querySelector('input[type="checkbox"]');
            
            card.addEventListener('click', (e) => {
                if (e.target !== checkbox) {
                    checkbox.checked = !checkbox.checked;
                    this.updateOptionCard(card, checkbox.checked);
                }
            });
            
            checkbox.addEventListener('change', () => {
                this.updateOptionCard(card, checkbox.checked);
            });
        });
    }

    updateOptionCard(card, isChecked) {
        if (isChecked) {
            card.style.borderColor = 'var(--primary-color)';
            card.style.background = 'rgba(102, 126, 234, 0.05)';
            card.style.transform = 'scale(1.02)';
        } else {
            card.style.borderColor = 'var(--border-color)';
            card.style.background = 'var(--bg-primary)';
            card.style.transform = 'scale(1)';
        }
    }

    validateURL(url) {
        const urlInput = document.getElementById('url');
        const isValid = this.isValidURL(url);
        
        if (url && !isValid) {
            urlInput.style.borderColor = 'var(--error-color)';
        } else if (url && isValid) {
            urlInput.style.borderColor = 'var(--success-color)';
        } else {
            urlInput.style.borderColor = 'var(--border-color)';
        }
    }

    isValidURL(string) {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    }

    async handleScrapeSubmit(e) {
        e.preventDefault();
        
        if (this.isLoading) return;
        
        const url = document.getElementById('url').value.trim();
        const options = Array.from(document.querySelectorAll('input[name="options"]:checked'))
                           .map(cb => cb.value);
        
        // Validation
        if (!url) {
            this.showError('Please enter a URL');
            return;
        }

        if (!this.isValidURL(url)) {
            this.showError('Please enter a valid URL (including http:// or https://)');
            return;
        }
        
        if (options.length === 0) {
            this.showError('Please select at least one scraping option');
            return;
        }

        // Start scraping process
        this.showLoading(true);
        this.hideResults();
        this.hideError();
        this.setButtonState(true);

        try {
            const result = await this.scrapeWebsite(url, options);
            
            if (result.success) {
                this.scrapedData = result;
                this.displayResults(result);
                this.showNotification('Scraping completed successfully!', 'success');
            } else {
                this.showError(result.error || 'Scraping failed');
            }
        } catch (error) {
            console.error('Scraping error:', error);
            this.showError('Network error: ' + error.message);
        } finally {
            this.showLoading(false);
            this.setButtonState(false);
        }
    }

    async scrapeWebsite(url, options) {
        const response = await fetch(`${this.apiBaseUrl}/scrape`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: url,
                options: options
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    displayResults(data) {
        // Animate results appearance
        this.showResults();
        
        // Display statistics
        this.displayStats(data.stats);
        
        // Display JSON output with syntax highlighting
        this.displayJSON(data);
        
        // Animate stat cards
        this.animateStatCards();
    }

    displayStats(stats) {
        const statsContainer = document.getElementById('statsGrid');
        if (!statsContainer || !stats) return;
        
        statsContainer.innerHTML = '';
        
        Object.entries(stats).forEach(([key, value]) => {
            const statCard = document.createElement('div');
            statCard.className = 'stat-card';
            statCard.innerHTML = `
                <span class="stat-number">${value.toLocaleString()}</span>
                <span class="stat-label">${this.formatStatLabel(key)}</span>
            `;
            
            // Add animation delay for staggered effect
            statCard.style.animationDelay = `${Object.keys(stats).indexOf(key) * 0.1}s`;
            
            statsContainer.appendChild(statCard);
        });
    }

    displayJSON(data) {
        const jsonOutput = document.getElementById('jsonOutput');
        if (!jsonOutput) return;
        
        const formattedJSON = JSON.stringify(data, null, 2);
        jsonOutput.textContent = formattedJSON;
        
        // Apply syntax highlighting
        this.applySyntaxHighlighting(jsonOutput);
    }

    applySyntaxHighlighting(element) {
        let html = element.textContent;
        
        // Simple syntax highlighting
        html = html.replace(/"([^"]+)":/g, '<span style="color: #60a5fa;">"$1"</span>:');
        html = html.replace(/: "([^"]*)"/g, ': <span style="color: #34d399;">"$1"</span>');
        html = html.replace(/: (\d+)/g, ': <span style="color: #fbbf24;">$1</span>');
        html = html.replace(/: (true|false|null)/g, ': <span style="color: #f87171;">$1</span>');
        
        element.innerHTML = html;
    }

    formatStatLabel(key) {
        return key.replace(/_/g, ' ')
                 .replace(/\b\w/g, l => l.toUpperCase())
                 .replace('Count', '')
                 .trim();
    }

    animateStatCards() {
        const statCards = document.querySelectorAll('.stat-card');
        statCards.forEach((card, index) => {
            setTimeout(() => {
                card.style.transform = 'translateY(0) scale(1)';
                card.style.opacity = '1';
            }, index * 100);
        });
    }

    async handleDownload() {
        try {
            this.showNotification('Preparing download...', 'info');
            
            const dataStr = JSON.stringify(this.scrapedData, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            
            const link = document.createElement('a');
            link.href = URL.createObjectURL(dataBlob);
            
            const timestamp = this.scrapedData.timestamp 
                ? this.scrapedData.timestamp.replace(/[:.]/g, '-') 
                : new Date().getTime();
            link.download = `scraped_data_${timestamp}.json`;
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            URL.revokeObjectURL(link.href);
            this.showNotification('File downloaded successfully!', 'success');
        } catch (error) {
            console.error('Download error:', error);
            this.showError('Failed to download file');
        }
    }

    async handleCopy() {
        try {
            const jsonText = JSON.stringify(this.scrapedData, null, 2);
            await navigator.clipboard.writeText(jsonText);
            this.showNotification('JSON data copied to clipboard!', 'success');
        } catch (error) {
            console.error('Copy error:', error);
            this.showError('Failed to copy to clipboard');
        }
    }

    formatJSON() {
        const jsonOutput = document.getElementById('jsonOutput');
        if (!jsonOutput) return;
        
        try {
            const parsed = JSON.parse(jsonOutput.textContent);
            const formatted = JSON.stringify(parsed, null, 2);
            jsonOutput.textContent = formatted;
            this.applySyntaxHighlighting(jsonOutput);
            this.showNotification('JSON formatted!', 'success');
        } catch (error) {
            this.showError('Invalid JSON format');
        }
    }

    collapseJSON() {
        const jsonOutput = document.getElementById('jsonOutput');
        if (!jsonOutput) return;
        
        try {
            const parsed = JSON.parse(jsonOutput.textContent);
            const collapsed = JSON.stringify(parsed);
            jsonOutput.textContent = collapsed;
            this.applySyntaxHighlighting(jsonOutput);
            this.showNotification('JSON collapsed!', 'success');
        } catch (error) {
            this.showError('Invalid JSON format');
        }
    }

    showLoading(show) {
        const loadingSection = document.getElementById('loadingSection');
        if (!loadingSection) return;
        
        if (show) {
            this.isLoading = true;
            loadingSection.style.display = 'block';
            this.startLoadingAnimation();
        } else {
            this.isLoading = false;
            loadingSection.style.display = 'none';
        }
    }

    startLoadingAnimation() {
        const messages = [
            'Fetching website data...',
            'Parsing HTML content...',
            'Extracting information...',
            'Processing results...',
            'Almost done...'
        ];
        
        const messageElement = document.getElementById('loadingMessage');
        const progressFill = document.getElementById('progressFill');
        
        let messageIndex = 0;
        const interval = setInterval(() => {
            if (!this.isLoading) {
                clearInterval(interval);
                return;
            }
            
            if (messageElement && messageIndex < messages.length) {
                messageElement.textContent = messages[messageIndex];
                messageIndex++;
            }
            
            if (progressFill) {
                const progress = Math.min((messageIndex / messages.length) * 100, 90);
                progressFill.style.width = `${progress}%`;
            }
        }, 800);
    }

    showResults() {
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.style.display = 'block';
            
            // Smooth scroll to results
            resultsSection.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }
    }

    hideResults() {
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.style.display = 'none';
        }
    }

    showError(message) {
        const errorSection = document.getElementById('errorSection');
        const errorMessage = document.getElementById('errorMessage');
        
        if (errorSection && errorMessage) {
            errorMessage.textContent = message;
            errorSection.style.display = 'block';
            
            // Smooth scroll to error
            errorSection.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
            });
        }
    }

    hideError() {
        const errorSection = document.getElementById('errorSection');
        if (errorSection) {
            errorSection.style.display = 'none';
        }
    }

    setButtonState(loading) {
        const button = document.getElementById('scrapeBtn');
        const icon = button?.querySelector('i');
        const text = button?.querySelector('span');
        
        if (button) {
            button.disabled = loading;
            
            if (loading) {
                if (icon) icon.className = 'fas fa-spinner fa-spin';
                if (text) text.textContent = 'Scraping...';
                button.style.opacity = '0.7';
            } else {
                if (icon) icon.className = 'fas fa-play';
                if (text) text.textContent = 'Start Scraping';
                button.style.opacity = '1';
            }
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
        `;
        
        // Style notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '100px',
            right: '20px',
            background: this.getNotificationColor(type),
            color: 'white',
            padding: '1rem 1.5rem',
            borderRadius: 'var(--radius-lg)',
            boxShadow: 'var(--shadow-lg)',
            zIndex: '10000',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            transform: 'translateX(400px)',
            transition: 'transform 0.3s ease'
        });
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 10);
        
        // Remove after delay
        setTimeout(() => {
            notification.style.transform = 'translateX(400px)';
            setTimeout(() => {
                if (notification.parentNode) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    getNotificationColor(type) {
        const colors = {
            success: 'var(--success-color)',
            error: 'var(--error-color)',
            warning: 'var(--warning-color)',
            info: 'var(--accent-color)'
        };
        return colors[type] || 'var(--accent-color)';
    }
}

// Global function for error retry
window.hideError = function() {
    const errorSection = document.getElementById('errorSection');
    if (errorSection) {
        errorSection.style.display = 'none';
    }
};

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new WebScraperApp();
});