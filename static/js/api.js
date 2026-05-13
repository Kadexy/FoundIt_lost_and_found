/**
 * API Service Module for Lost and Found Application
 * Handles all API communications with the backend
 */

const API = {
    BASE_URL: '/api',

    normalizeResults(payload) {
        if (Array.isArray(payload)) {
            return payload;
        }

        if (payload && Array.isArray(payload.results)) {
            return payload.results;
        }

        return [];
    },

    buildItemEndpoint(itemType, itemId = '') {
        if (itemType !== 'lost' && itemType !== 'found') {
            throw new Error('Item type must be "lost" or "found".');
        }

        return itemId ? `/items/${itemType}/${itemId}/` : `/items/${itemType}/`;
    },
    
    /**
     * Initialize the API module with base URL
     */
    init(baseUrl = '') {
        if (baseUrl) {
            this.BASE_URL = baseUrl;
        }
    },

    /**
     * Make HTTP requests with automatic token handling
     */
    async request(endpoint, options = {}) {
        const url = `${this.BASE_URL}${endpoint}`;
        console.log(`API Request: ${options.method || 'GET'} ${url}`);

        const isFormData = options.body instanceof FormData;
        const headers = {
            'Cache-Control': 'no-cache',
            ...options.headers
        };

        if (!isFormData && !headers['Content-Type']) {
            headers['Content-Type'] = 'application/json';
        }

        // Add Authorization header if token exists
        const token = localStorage.getItem('access_token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            console.log(`API Response: ${response.status} ${response.statusText} from ${url}`);

            // Handle 401 Unauthorized - refresh token or redirect to login
            if (response.status === 401) {
                const refreshToken = localStorage.getItem('refresh_token');
                if (refreshToken && endpoint !== '/user/login/' && endpoint !== '/user/signup/' && endpoint !== '/user/logout/') {
                    const refreshed = await this.refreshToken();
                    if (refreshed) {
                        return this.request(endpoint, options); // Retry request
                    }
                }
                this.clearSession();
                throw new Error('Unauthorized access. Please log in again.');
            }

            // Handle 403 Forbidden
            if (response.status === 403) {
                throw new Error('Access denied. You do not have permission to perform this action.');
            }

            // Read the response body once, then parse it safely.
            const rawBody = await response.text();
            let data = null;

            if (rawBody) {
                try {
                    data = JSON.parse(rawBody);
                    console.log('Response data:', data);
                } catch (jsonError) {
                    console.error('Non-JSON response:', rawBody);
                    console.error('JSON parse error:', jsonError, 'Response status:', response.status);
                    if (!response.ok) {
                        throw new Error(`Server error (${response.status}): ${response.statusText} - ${rawBody.substring(0, 200)}`);
                    }
                    throw new Error('Unexpected server response format');
                }
            }

            if (!response.ok) {
                // Build detailed error message from DRF validation errors
                console.log('Error response data:', data);
                let errorMsg = (data && (data.message || data.detail)) || `API request failed (${response.status})`;
                if (data) {
                    const fieldErrors = [];
                    for (const [field, errors] of Object.entries(data)) {
                        if (Array.isArray(errors)) {
                            fieldErrors.push(`${field}: ${errors.join(', ')}`);
                        } else if (typeof errors === 'string') {
                            fieldErrors.push(`${field}: ${errors}`);
                        }
                    }
                    if (fieldErrors.length > 0) {
                        errorMsg = fieldErrors.join('; ');
                    }
                }
                throw new Error(errorMsg);
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    // ==================== AUTHENTICATION ENDPOINTS ====================

    /**
     * Sign up a new user
     */
    async signup(userData) {
        const body = userData instanceof FormData ? userData : JSON.stringify(userData);
        return this.request('/user/signup/', {
            method: 'POST',
            body
        });
    },

    /**
     * Login user
     */
    async login(email, password) {
        this.clearSession();

        const response = await this.request('/user/login/', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });

        if (!response || !response.tokens) {
            throw new Error('Login failed. Please check your credentials.');
        }
        
        localStorage.setItem('access_token', response.tokens.access);
        localStorage.setItem('refresh_token', response.tokens.refresh);
        localStorage.setItem('user_id', response.id);
        localStorage.setItem('user_email', response.email);
        return response;
    },

    /**
     * Refresh access token
     */
    async refreshToken() {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) return false;

        try {
            const response = await fetch(`${this.BASE_URL}/user/refresh-token/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh: refreshToken })
            });

            const data = await response.json();
            if (response.ok && data.access) {
                localStorage.setItem('access_token', data.access);
                return true;
            }
            return false;
        } catch (error) {
            console.error('Token refresh failed:', error);
            return false;
        }
    },

    /**
     * Logout user
     */
    async logout() {
        const refreshToken = localStorage.getItem('refresh_token');
        console.log('Starting logout. Refresh token exists:', !!refreshToken);
        try {
            if (refreshToken) {
                const response = await this.request('/user/logout/', {
                    method: 'POST',
                    body: JSON.stringify({ refresh: refreshToken })
                });
                console.log('Logout API response:', response);
            }
        } catch (error) {
            console.error('Logout API call failed:', error);
        }
        console.log('Clearing session and redirecting to login');
        this.clearSession();
        window.location.href = '/login/';
    },

    /**
     * Clear stored session data
     */
    clearSession() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_id');
        localStorage.removeItem('user_email');
    },

    /**
     * Parse a JWT token and return its payload
     */
    parseJwt(token) {
        try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(atob(base64).split('').map((c) => {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join(''));
            return JSON.parse(jsonPayload);
        } catch (error) {
            return null;
        }
    },

    /**
     * Check if user is authenticated and token is valid
     */
    isAuthenticated() {
        const token = localStorage.getItem('access_token');
        if (!token) return false;

        const payload = this.parseJwt(token);
        if (!payload || !payload.exp) {
            this.clearSession();
            return false;
        }

        const now = Math.floor(Date.now() / 1000);
        if (payload.exp <= now) {
            this.clearSession();
            return false;
        }

        return true;
    },

    /**
     * Get current user info
     */
    getCurrentUser() {
        return {
            id: localStorage.getItem('user_id'),
            email: localStorage.getItem('user_email')
        };
    },

    /**
     * Get the authenticated user's profile
     */
    async getProfile() {
        return this.request('/user/profile/', {
            method: 'GET'
        });
    },

    async changePassword(passwordData) {
        return this.request('/user/change-password/', {
            method: 'POST',
            body: JSON.stringify(passwordData)
        });
    },

    async deleteAccount(password) {
        return this.request('/user/delete-account/', {
            method: 'POST',
            body: JSON.stringify({ password })
        });
    },

    async updateProfilePicture(file) {
        const formData = new FormData();
        formData.append('profile_picture', file);

        return this.request('/user/profile-picture/', {
            method: 'POST',
            body: formData
        });
    },

    async resendVerificationEmail(email) {
        return this.request('/user/resend-verification/', {
            method: 'POST',
            body: JSON.stringify({ email })
        });
    },

    // ==================== ITEMS ENDPOINTS ====================

    /**
     * Get lost items list
     */
    async getLostItems() {
        return this.request('/items/lost/', {
            method: 'GET'
        });
    },

    /**
     * Get found items list
     */
    async getFoundItems() {
        return this.request('/items/found/', {
            method: 'GET'
        });
    },

    /**
     * Get all categories
     */
    async getCategories() {
        return this.request('/items/categories/', {
            method: 'GET'
        });
    },

    /**
     * Get all locations
     */
    async getLocations() {
        return this.request('/items/locations/', {
            method: 'GET'
        });
    },

    /**
     * Create a new item (lost or found)
     */
    async createItem(itemData) {
        console.log('createItem called with:', itemData);
        
        // Determine the correct endpoint based on status - default to 'found' if not provided
        const itemStatus = (itemData.status === 'lost' || itemData.status === 'found') 
            ? itemData.status 
            : 'found';
        
        const endpoint = this.buildItemEndpoint(itemStatus);
        
        console.log('Using endpoint:', endpoint, 'for status:', itemStatus);
        
        // Remove status from the data sent to API (not needed for the serializer)
        const { status, ...apiData } = itemData;
        
        let processedData = { ...apiData };
        if (processedData.location_id) {
            processedData.location_id = parseInt(processedData.location_id, 10);
        }
        if (itemStatus === 'found' && processedData.dropped_location_id) {
            processedData.dropped_location_id = parseInt(processedData.dropped_location_id, 10);
        }
        
        // Convert category_id to integer
        if (processedData.category_id) {
            processedData.category_id = parseInt(processedData.category_id, 10);
        }
        
        console.log('Sending data to', endpoint, ':', processedData);

        const formData = new FormData();
        for (const [key, value] of Object.entries(processedData)) {
            if (value !== null && value !== undefined && value !== '') {
                formData.append(key, value);
            }
        }

        return this.request(endpoint, {
            method: 'POST',
            body: formData
        });
    },

    /**
     * Get single item details
     */
    async getItem(itemId, itemType = null) {
        if (itemType === 'lost' || itemType === 'found') {
            return this.request(`/items/${itemType}/${itemId}/`, {
                method: 'GET'
            });
        }

        try {
            return await this.request(`/items/lost/${itemId}/`, {
                method: 'GET'
            });
        } catch (lostError) {
            return this.request(`/items/found/${itemId}/`, {
                method: 'GET'
            });
        }
    },

    /**
     * Update an item
     */
    async updateItem(itemId, itemData, itemType = null) {
        const resolvedType = itemType || itemData.item_type || itemData.type || itemData.status;
        const endpoint = this.buildItemEndpoint(resolvedType, itemId);
        const formData = new FormData();
        
        for (const key in itemData) {
            if (['item_type', 'type', 'status'].includes(key)) {
                continue;
            }

            if (itemData[key] !== null && itemData[key] !== undefined) {
                formData.append(key, itemData[key]);
            }
        }

        return this.request(endpoint, {
            method: 'PATCH',
            body: formData
        });
    },

    /**
     * Delete an item
     */
    async deleteItem(itemId, itemType) {
        return this.request(this.buildItemEndpoint(itemType, itemId), {
            method: 'DELETE'
        });
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = API;
}
