# Lost & Found Application - Quick Start Guide

## ⚡ 5-Minute Setup

### 1. Install Dependencies
```bash
cd "LOST AND FOUND"
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. (Optional) Create Admin User
```bash
python manage.py createsuperuser
```

### 4. Create Initial Data
```bash
python manage.py shell
```
Then run:
```python
from items.models import Category, Location

# Categories
categories = ['Phone', 'Wallet', 'ID Card', 'Keys', 'Laptop', 'iPad', 'Tablet', 'Book', 'Other']
for cat in categories:
    Category.objects.get_or_create(name=cat)

# Locations
locations = ['Library', 'Cafeteria', 'Main Hall', 'IT Building', 'Science Block', 'Student Center']
for loc in locations:
    Location.objects.get_or_create(name=loc)

# Exit
exit()
```

### 5. Start Server
```bash
python manage.py runserver
```

### 6. Access Application
- **Landing Page**: http://localhost:8000
- **API Docs**: http://localhost:8000 (Swagger UI)
- **Sign Up**: http://localhost:8000/signup.html
- **Login**: http://localhost:8000/login.html

## 🎯 First Use Steps

### Create Account
1. Go to http://localhost:8000/signup.html
2. Fill in your details
3. Select "Student" as user type and enter your student ID
4. Click "Create Account"

### Login
1. Go to http://localhost:8000/login.html
2. Enter your email and password
3. Click "Sign In"

### Browse Items
1. Click "Browse Lost Items" or "Browse Found Items"
2. Use filters to search
3. Click any item to see details

### Report an Item
1. Click "Report Item"
2. Select "Lost" or "Found"
3. Fill in details about the item
4. Upload a photo (optional)
5. Click "Report Item"

## 🛠️ Project Structure

```
templates/          # HTML pages
├── index.html      # Landing page
├── login.html      # Login page
├── signup.html     # Sign up page
├── dashboard.html  # Main dashboard
├── items-lost.html # Browse lost items
├── items-found.html# Browse found items
├── report.html     # Report item
├── item-detail.html# Item details
└── profile.html    # User profile

static/
├── css/
│   └── modern.css  # Main stylesheet
└── js/
    ├── api.js      # API service
    └── ui.js       # UI utilities
```

## 📱 Frontend Pages

| Page | URL | Purpose |
|------|-----|---------|
| Landing | `/` | Home page with features |
| Login | `/login.html` | User login |
| Sign Up | `/signup.html` | New account creation |
| Dashboard | `/dashboard.html` | Main app interface |
| Lost Items | `/items-lost.html` | Browse lost items |
| Found Items | `/items-found.html` | Browse found items |
| Report | `/report.html` | Report new item |
| Item Detail | `/item-detail.html?id={id}` | View item details |
| Profile | `/profile.html` | User profile |

## 🔌 API Endpoints

### Authentication
- `POST /user/signup` - Register
- `POST /user/login` - Login
- `POST /user/logout` - Logout
- `POST /user/refresh-token/` - Refresh JWT

### Items
- `GET /items/lost/` - List lost items
- `GET /items/found/` - List found items
- `POST /items/` - Create item
- `GET /items/{id}/` - Item details
- `PATCH /items/{id}/` - Update item
- `DELETE /items/{id}/` - Delete item

### Data
- `GET /items/categories/` - All categories
- `GET /items/locations/` - All locations

## 🔐 User Types

- **Student**: Can report items, view matching items
- **Staff**: Can report items, see more inventory
- **Admin**: Full system access

## 💡 Example Test Flow

### Test 1: Register & Login
```
1. Go to /signup.html
2. Create account: 
   - Email: test@example.com
   - Name: Test User
   - Student ID: STU001
3. Login with above credentials
4. See dashboard
```

### Test 2: Report Item
```
1. Login
2. Click "Report Item"
3. Status: Lost
4. Category: Phone
5. Title: Black iPhone
6. Description: Lost near library
7. Location: Library
8. Submit
```

### Test 3: Browse & Search
```
1. Click "Browse Lost Items"
2. Filter by "Phone" category
3. Search "iPhone"
4. Click "View Details"
5. See full item information
```

## 🎨 Customization

### Change Colors
Edit `static/css/modern.css` CSS variables:
```css
:root {
    --primary-color: #2c3e50;
    --secondary-color: #3498db;
    --success-color: #27ae60;
    --danger-color: #e74c3c;
}
```

### Add Navigation Links
Edit any HTML template's `<nav>` section:
```html
<nav>
    <ul>
        <li><a href="/new-page.html">New Link</a></li>
    </ul>
</nav>
```

## 📊 Key Features

✅ User Authentication with JWT
✅ Item Reporting (Lost/Found)
✅ Smart Matching Algorithm
✅ Category & Location Filtering
✅ Search Functionality
✅ User Profiles
✅ Item Details with Images
✅ Responsive Design
✅ Modern UI
✅ API Documentation

## 🐛 Troubleshooting

### Port Already in Use
```bash
python manage.py runserver 8001
```

### Clear Cache
```bash
python manage.py collectstatic --clear
```

### Reset Database
```bash
python manage.py flush  # Warning: Deletes all data!
python manage.py migrate
```

### Check Migration Status
```bash
python manage.py showmigrations
```

## 📚 Full Documentation

See `FRONTEND_SETUP.md` for complete documentation including:
- Detailed setup instructions
- API endpoint documentation
- Backend configuration
- Deployment guide
- Advanced features
- Testing procedures

## 🚀 Production Deployment

Before deploying:
1. Set `DEBUG = False` in settings
2. Add production domain to `ALLOWED_HOSTS`
3. Use environment variables for `SECRET_KEY`
4. Configure proper database
5. Set up HTTPS
6. Configure allowed CORS origins

## 📞 Support

- Check browser console: F12 → Console tab
- View server logs: Terminal where runserver is running
- Check API docs: http://localhost:8000

## 📝 Notes

- Test user credentials should be created via signup
- Admin user can be created with `python manage.py createsuperuser`
- Images are stored in `media/` folder
- Database is SQLite by default (`db.sqlite3`)
- Change to PostgreSQL/MySQL for production

---

**Ready to go!** Start with `/signup.html` and enjoy the application! 🎉
