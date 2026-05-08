# Lost & Found Application - Setup & Integration Guide

## Overview
This is a full-stack Lost and Found application with a Django REST API backend and a modern plain JavaScript frontend. The application helps communities reunite lost items with their owners through intelligent matching and community collaboration.

## Architecture

### Backend
- **Framework**: Django 6.0.3
- **API**: Django REST Framework with JWT authentication
- **Authentication**: JWT tokens with refresh mechanism
- **API Documentation**: Swagger UI at `/` endpoint

### Frontend
- **Technology**: Plain JavaScript (Vanilla JS)
- **Styling**: Modern CSS with responsive design
- **Architecture**: Modular JavaScript with separate modules for API, UI utilities
- **Pages**: Login, Signup, Dashboard, Browse Items, Report Items, Item Details, User Profile

## Project Structure

```
LOST AND FOUND/
├── db.sqlite3
├── manage.py
├── requirements.txt
├── env/                           # Virtual environment
├── foundIt/                       # Main Django project
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── items/                         # Items app
│   ├── models.py                 # Item, Category, Location models
│   ├── views.py                  # API views
│   ├── serializers.py            # DRF serializers
│   ├── urls.py
│   └── migrations/
├── users/                         # Users app
│   ├── models.py                 # CustomUser model
│   ├── views.py                  # Authentication views
│   ├── serializers.py
│   ├── urls.py
│   └── migrations/
├── utils/                         # Utility functions
│   └── pagination.py
├── templates/                     # HTML templates
│   ├── index.html               # Landing page
│   ├── login.html               # Login page
│   ├── signup.html              # Sign up page
│   ├── dashboard.html           # Main dashboard
│   ├── items-lost.html          # Browse lost items
│   ├── items-found.html         # Browse found items
│   ├── report.html              # Report item page
│   ├── item-detail.html         # Item details page
│   └── profile.html             # User profile page
├── static/                        # Static files
│   ├── css/
│   │   └── modern.css           # Main stylesheet
│   └── js/
│       ├── api.js               # API service module
│       └── ui.js                # UI utilities module
└── media/                         # User uploaded files
    └── items/                    # Item images
    └── profile_picture/          # User profile pictures
```

## Backend API Endpoints

### Authentication
- `POST /user/signup` - Create new user account
- `POST /user/login` - User login (returns JWT tokens)
- `POST /user/refresh-token/` - Refresh access token
- `POST /user/logout` - User logout (blacklist token)

### Items
- `GET /items/lost/` - Get list of lost items (filtered by user permissions)
- `GET /items/found/` - Get list of found items (privacy-first matching for students)
- `GET /items/` - Get all items (requires authentication)
- `POST /items/` - Create new item
- `GET /items/{id}/` - Get item details
- `PATCH /items/{id}/` - Update item
- `DELETE /items/{id}/` - Delete item

### Categories & Locations
- `GET /items/categories/` - Get all categories
- `POST /items/categories/` - Create new category
- `GET /items/locations/` - Get all locations
- `POST /items/locations/` - Create new location

## Frontend Features

### 1. Authentication
- User registration (Student/Staff/Admin)
- Secure JWT-based login
- Token refresh mechanism
- Logout functionality

### 2. Dashboard
- Overview of recent lost and found items
- Quick access to main features
- User statistics

### 3. Browse Items
- View lost items
- View found items
- Filter by category, location, or search term
- View item details including photos and specifications

### 4. Report Items
- Report lost items with full details
- Report found items
- Upload item photos
- Add item specifications (brand, model, serial number, etc.)
- Select location and category

### 5. Item Details
- View complete item information
- See if item has been matched
- Contact reporter details (when available)
- Item status (Lost/Found/Claimed/Returned)

### 6. User Profile
- View personal information
- See reported items statistics
- Manage account settings
- View all items reported by user

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Step 1: Set Up Virtual Environment
```bash
cd "LOST AND FOUND"
python -m venv env
# On Windows
env\Scripts\activate
# On macOS/Linux
source env/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run Migrations
```bash
python manage.py migrate
```

### Step 4: Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### Step 5: Create Initial Data (Optional)
```bash
python manage.py shell
```
Then in the shell:
```python
from items.models import Category, Location

# Create categories
categories = [
    'Phone', 'Wallet', 'ID Card', 'Keys', 'Laptop', 
    'iPad', 'Tablet', 'Book', 'Other'
]
for cat_name in categories:
    Category.objects.get_or_create(name=cat_name)

# Create locations
locations = [
    'Library', 'Cafeteria', 'Main Hall', 'IT Building', 
    'Science Block', 'Student Center', 'Parking Lot'
]
for loc_name in locations:
    Location.objects.get_or_create(name=loc_name)
```

### Step 6: Run Development Server
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## Frontend Usage

### Landing Page
- Visit `http://localhost:8000` to see the landing page
- Click "Get Started" or "Sign In" to proceed

### User Registration
1. Click "Sign Up" or go to `/signup.html`
2. Fill in your details (First Name, Last Name, Email, Phone, Gender, User Type)
3. If Student/Staff, provide your ID
4. Create a password
5. Click "Create Account"

### User Login
1. Go to `/login.html`
2. Enter your email and password
3. Click "Sign In"

### Dashboard
- View recent lost and found items
- Access main features through action cards
- Quick links to browse items, report items, and view profile

### Browsing Items
1. Click "Browse Lost Items" or "Browse Found Items"
2. Use filters to narrow results (category, location, search)
3. Click "View Details" on any item to see full information

### Reporting an Item
1. Click "Report Item" on dashboard
2. Select item status (Lost/Found)
3. Choose category and provide title
4. Add description and other details
5. Select location (optional)
6. Upload photo (optional)
7. Click "Report Item"

### View Item Details
1. Click "View Details" on any item card
2. See all item information
3. If item is matched, see status
4. Contact information available if you're authorized

### User Profile
1. Click "Profile" in navigation
2. View your personal information
3. See your reported items
4. Access account settings

## Key Features & How They Work

### Privacy-First Matching
- Students can only see found items that match their lost items
- Admin/Staff can see full inventory for management
- Intelligent scoring algorithm matches items based on:
  - Category (30 points)
  - Color (20 points)
  - Description similarity (20 points)
  - Location similarity (15 points)
  - Brand match (8 points)
  - Model match (7 points)
  - Time proximity (5-10 points)

### JWT Authentication
- Access token expires in 24 hours
- Automatic token refresh if available
- Refresh token expires in 3 days
- Token blacklist for secure logout

### Data Validation
- Email uniqueness validation
- Phone number uniqueness validation
- Student/Staff ID uniqueness validation
- Password strength requirements

## Backend Configuration

### Environment Variables
The following settings are in `foundIt/settings.py`. For production, use environment variables:
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (False in production)
- `ALLOWED_HOSTS` - Allowed hosts list

### JWT Configuration
Located in `foundIt/settings.py`:
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=3),
}
```

### CORS Configuration
- Currently allows all origins: `CORS_ALLOW_ALL_ORIGINS = True`
- For production, specify allowed origins

### Static Files
- CSS files: `static/css/`
- JavaScript files: `static/js/`
- Media uploads: `media/`

## Frontend JavaScript Modules

### API Module (`static/js/api.js`)
Handles all API communications with automatic token handling:
- Token refresh on 401 Unauthorized
- Error handling and logging
- Request/Response formatting
- Authentication methods
- Items CRUD operations

**Key Methods:**
```javascript
API.init(baseUrl)              // Initialize with base URL
API.login(email, password)     // Login user
API.signup(userData)           // Sign up new user
API.logout()                   // Logout user
API.getLostItems()            // Get lost items list
API.getFoundItems()           // Get found items list
API.getCategories()           // Get item categories
API.getLocations()            // Get locations
API.createItem(itemData)      // Create new item
API.getItem(itemId)           // Get item details
API.updateItem(itemId, data)  // Update item
API.deleteItem(itemId)        // Delete item
```

### UI Module (`static/js/ui.js`)
Provides UI utilities and helper functions:
- Message/toast notifications
- Date formatting
- Form utilities
- Item card rendering
- Loading spinner
- Authentication checks

**Key Methods:**
```javascript
UI.showMessage(message, type)     // Show notification
UI.formatDate(dateString)         // Format date to readable
UI.timeAgo(dateString)            // Get relative time (e.g., "2 days ago")
UI.renderItemCard(item, type)     // Generate HTML for item card
UI.getFormData(formElement)       // Get form data as object
UI.requireAuth()                   // Check authentication
UI.redirect(url)                  // Redirect to page
```

## Testing the Application

### Test User Scenarios

#### Scenario 1: Register and Login
1. Go to signup page
2. Create a student account with Student ID
3. Login with created credentials
4. Verify dashboard loads

#### Scenario 2: Report Lost Item
1. Login as student
2. Go to Report Item
3. Select "Lost" status
4. Fill in all details
5. Submit
6. Verify item appears in Lost Items list

#### Scenario 3: Matching
1. Create a lost item (phone, black, location A)
2. Create a found item in same category with similar details
3. System should auto-match the items
4. Check matched status in item details

#### Scenario 4: Filter and Search
1. Go to Lost Items or Found Items
2. Filter by category
3. Search by keyword
4. Verify results are filtered correctly

## Troubleshooting

### Common Issues

1. **CORS Error**
   - Frontend can't reach backend
   - Solution: Ensure `CORS_ALLOW_ALL_ORIGINS = True` in settings

2. **401 Unauthorized**
   - Token expired or invalid
   - Solution: System will auto-refresh or redirect to login

3. **Images Not Loading**
   - Missing MEDIA_URL configuration
   - Solution: Check `MEDIA_URL` and `MEDIA_ROOT` in settings

4. **API Endpoints Not Found**
   - Check URLs configuration in both apps
   - Verify router is properly registered

5. **Form Submission Fails**
   - Check browser console for errors
   - Verify all required fields are filled
   - Check API response in Network tab

## Production Deployment

### Before Going to Production

1. **Security**
   - Set `DEBUG = False`
   - Use environment variables for sensitive data
   - Set secure `SECRET_KEY`
   - Update `ALLOWED_HOSTS`
   - Use HTTPS

2. **Database**
   - Switch from SQLite to PostgreSQL/MySQL
   - Set up proper backups

3. **Static Files**
   - Collect static files: `python manage.py collectstatic`
   - Serve with CDN or web server

4. **Email**
   - Configure email backend for notifications

5. **API Rate Limiting**
   - Add throttling to REST framework settings

6. **Logging**
   - Set up proper logging configuration

## API Documentation

Access the interactive Swagger API documentation at:
```
http://localhost:8000/
```

This provides a complete interactive interface to test all API endpoints.

## Support & Contribution

For issues or questions:
1. Check the API documentation at `/`
2. Review browser console for errors
3. Check server logs: `python manage.py runserver`

## License

This project is provided as-is for educational purposes.

---

**Version**: 1.0
**Last Updated**: 2024
**Created with**: Django, Django REST Framework, Plain JavaScript
