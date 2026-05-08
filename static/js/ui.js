/**
 * Utility Module for UI and Common Functions
 */

const UI = {
    /**
     * Show a message toast/alert
     */
    showMessage(message, type = 'error') {
        const messageDiv = document.getElementById('message-container');
        if (!messageDiv) {
            const container = document.createElement('div');
            container.id = 'message-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                max-width: 400px;
            `;
            document.body.appendChild(container);
        }

        const messagePart = document.createElement('div');
        messagePart.className = `message message-${type}`;
        messagePart.innerHTML = `
            <div style="padding: 15px; background: ${type === 'success' ? '#4CAF50' : type === 'warning' ? '#ff9800' : '#f44336'}; color: white; border-radius: 4px; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
                ${message}
            </div>
        `;

        document.getElementById('message-container').appendChild(messagePart);

        setTimeout(() => {
            messagePart.remove();
        }, 4000);
    },

    showFormMessage(message, type = 'error', containerId = 'loginMessage') {
        const container = document.getElementById(containerId);
        if (!container) {
            this.showMessage(message, type);
            return;
        }
        container.innerHTML = `
            <div style="padding: 15px; background: ${type === 'success' ? '#4CAF50' : type === 'warning' ? '#ff9800' : '#f44336'}; color: white; border-radius: 4px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.12);">
                ${message}
            </div>
        `;
        setTimeout(() => {
            container.innerHTML = '';
        }, 5000);
    },

    /**
     * Format date to readable format
     */
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    },

    /**
     * Format date to short format
     */
    formatDateShort(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString();
    },

    /**
     * Calculate time ago (e.g., "2 days ago")
     */
    timeAgo(dateString) {
        const date = new Date(dateString);
        const seconds = Math.floor((new Date() - date) / 1000);

        let interval = seconds / 31536000;
        if (interval > 1) return Math.floor(interval) + ' years ago';

        interval = seconds / 2592000;
        if (interval > 1) return Math.floor(interval) + ' months ago';

        interval = seconds / 86400;
        if (interval > 1) return Math.floor(interval) + ' days ago';

        interval = seconds / 3600;
        if (interval > 1) return Math.floor(interval) + ' hours ago';

        interval = seconds / 60;
        if (interval > 1) return Math.floor(interval) + ' minutes ago';

        return Math.floor(seconds) + ' seconds ago';
    },

    /**
     * Show loading spinner
     */
    showLoading(element, show = true) {
        if (show) {
            element.innerHTML = '<div class="spinner"></div><p>Loading...</p>';
            element.classList.add('loading');
        } else {
            element.classList.remove('loading');
        }
    },

    /**
     * Render item card HTML
     */
    renderItemCard(item, type = 'lost') {
        const statusClass = `status-${item.status}`;
        const imageUrl = item.image ? item.image : '/static/assets/img/placeholder.png';
        const itemType = type || (item.dropped_location !== undefined ? 'found' : 'lost');
        const itemLocation = item.location || item.dropped_location;
        
        return `
            <div class="item-card" data-item-id="${item.id}" data-item-type="${itemType}">
                <div class="item-image">
                    <img src="${imageUrl}" alt="${item.title}" onerror="this.src='/static/assets/img/placeholder.png'">
                    <span class="item-status ${statusClass}">${item.status.toUpperCase()}</span>
                </div>
                <div class="item-content">
                    <h3 class="item-title">${item.title}</h3>
                    <p class="item-category"><strong>Category:</strong> ${item.category.name}</p>
                    <p class="item-location"><strong>Location:</strong> ${itemLocation ? itemLocation.name : 'Not specified'}</p>
                    <p class="item-date">${UI.timeAgo(item.date_reported)}</p>
                    <button class="btn-details" data-item-id="${item.id}" data-item-type="${itemType}">View Details</button>
                </div>
            </div>
        `;
    },

    /**
     * Create a form field
     */
    createFormField(label, type, name, required = false, options = null) {
        const id = `field-${name}`;
        let fieldHTML = `
            <div class="form-group">
                <label for="${id}">${label}${required ? ' <span class="required">*</span>' : ''}</label>
        `;

        if (type === 'select' && options) {
            fieldHTML += `
                <select id="${id}" name="${name}" ${required ? 'required' : ''}>
                    <option value="">Select ${label}</option>
                    ${options.map(opt => `<option value="${opt.id}">${opt.name}</option>`).join('')}
                </select>
            `;
        } else if (type === 'textarea') {
            fieldHTML += `
                <textarea id="${id}" name="${name}" ${required ? 'required' : ''} rows="4"></textarea>
            `;
        } else {
            fieldHTML += `
                <input type="${type}" id="${id}" name="${name}" ${required ? 'required' : ''}>
            `;
        }

        fieldHTML += `</div>`;
        return fieldHTML;
    },

    /**
     * Get form data as object
     */
    getFormData(formElement) {
        const formData = new FormData(formElement);
        const data = {};
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        return data;
    },

    /**
     * Redirect to page
     */
    redirect(url) {
        window.location.href = url;
    },

    /**
     * Check if user is authenticated, redirect if not
     */
    requireAuth() {
        if (!API.isAuthenticated()) {
            this.redirect('/login/');
            return false;
        }
        return true;
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UI;
}
