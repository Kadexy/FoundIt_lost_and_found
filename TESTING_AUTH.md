# Authentication & Authorization Testing Guide

## Quick Verification Steps

### Step 1: Verify Email Backend Works
```bash
python manage.py shell
```

Then in the shell:
```python
from users.models import CustomUser
from django.contrib.auth import authenticate

# Create a test user
user = CustomUser.objects.create_user(
    firstname='Test',
    lastname='User',
    email='test@example.com',
    phone='1234567890',
    gender='MALE',
    user_type='STUDENTS',
    student_id='STU001',
    password='testpass123'
)

# Test authentication
authenticated_user = authenticate(username='test@example.com', password='testpass123')
print(f"Authentication successful: {authenticated_user is not None}")
print(f"User email: {authenticated_user.email if authenticated_user else 'Failed'}")

exit()
```

### Step 2: Test API Authentication

#### Start the server:
```bash
python manage.py runserver
```

#### Test 1: Access API without token (should fail with 401)
```bash
curl -X GET http://localhost:8000/items/categories/
# Expected: {"detail":"Authentication credentials were not provided."}
```

#### Test 2: Login and get tokens
```bash
curl -X POST http://localhost:8000/user/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'

# Expected response:
# {
#   "id": "STU001",
#   "email": "test@example.com",
#   "user_type": "STUDENTS",
#   "tokens": {
#     "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#     "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
#   }
# }
```

#### Test 3: Access API with token (should succeed with 200)
```bash
# Replace {ACCESS_TOKEN} with the token from Test 2
curl -X GET http://localhost:8000/items/categories/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"

# Expected: List of categories
```

#### Test 4: Test item ownership
```bash
# Create an item as student1
curl -X POST http://localhost:8000/items/ \
  -H "Authorization: Bearer {STUDENT1_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "lost",
    "category_id": 1,
    "title": "Test Item",
    "description": "Test description",
    "location_id": 1
  }'

# Try to delete as student2 (should fail with 403)
curl -X DELETE http://localhost:8000/items/{ITEM_ID}/ \
  -H "Authorization: Bearer {STUDENT2_ACCESS_TOKEN}"

# Expected: {"detail": "You do not have permission to delete this item."}

# Try to delete as staff (should succeed with 204)
curl -X DELETE http://localhost:8000/items/{ITEM_ID}/ \
  -H "Authorization: Bearer {STAFF_ACCESS_TOKEN}"

# Expected: 204 No Content
```

#### Test 5: Test logout
```bash
curl -X POST http://localhost:8000/user/logout \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "{REFRESH_TOKEN}"
  }'

# Expected: {"detail": "Successfully logged out."}

# Try to use refresh token after logout (should fail)
curl -X POST http://localhost:8000/user/refresh-token/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "{REFRESH_TOKEN}"
  }'

# Expected: TokenError - token is blacklisted
```

---

## Automated Testing with Python

### Create a test script: `test_auth.py`

```python
import requests
import json

BASE_URL = 'http://localhost:8000'

class AuthTester:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.student_id = None

    def test_signup(self):
        """Test user registration"""
        print("\n=== Testing Sign Up ===")
        response = requests.post(
            f'{BASE_URL}/user/signup',
            json={
                'firstname': 'Test',
                'lastname': 'User',
                'email': f'test{hash(id(self))}@example.com',
                'phone': f'555{hash(id(self))%10000}',
                'gender': 'MALE',
                'user_type': 'STUDENTS',
                'student_id': f'STU{hash(id(self))%10000}',
                'password': 'SecurePass123!'
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 201

    def test_login(self, email, password):
        """Test user login"""
        print("\n=== Testing Login ===")
        response = requests.post(
            f'{BASE_URL}/user/login',
            json={
                'email': email,
                'password': password
            }
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200:
            self.access_token = data['tokens']['access']
            self.refresh_token = data['tokens']['refresh']
            self.student_id = data['id']
            return True
        return False

    def test_unauthenticated_access(self):
        """Test accessing API without token"""
        print("\n=== Testing Unauthenticated Access ===")
        response = requests.get(f'{BASE_URL}/items/categories/')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 401

    def test_authenticated_access(self):
        """Test accessing API with valid token"""
        print("\n=== Testing Authenticated Access ===")
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(f'{BASE_URL}/items/categories/', headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200

    def test_invalid_token(self):
        """Test accessing API with invalid token"""
        print("\n=== Testing Invalid Token ===")
        headers = {'Authorization': 'Bearer invalid_token_12345'}
        response = requests.get(f'{BASE_URL}/items/categories/', headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 401

    def test_logout(self):
        """Test user logout"""
        print("\n=== Testing Logout ===")
        response = requests.post(
            f'{BASE_URL}/user/logout',
            json={'refresh': self.refresh_token},
            headers={'Authorization': f'Bearer {self.access_token}'}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200

    def run_all_tests(self, email, password):
        """Run all authentication tests"""
        print("Starting Authentication & Authorization Tests...")
        
        tests = [
            ("Unauthenticated Access", self.test_unauthenticated_access),
            ("User Login", lambda: self.test_login(email, password)),
            ("Authenticated Access", self.test_authenticated_access),
            ("Invalid Token", self.test_invalid_token),
            ("Logout", self.test_logout),
        ]
        
        results = {}
        for test_name, test_func in tests:
            try:
                result = test_func()
                results[test_name] = "✅ PASSED" if result else "❌ FAILED"
            except Exception as e:
                results[test_name] = f"❌ ERROR: {str(e)}"
        
        print("\n=== Test Summary ===")
        for test_name, result in results.items():
            print(f"{test_name}: {result}")

# Usage
if __name__ == '__main__':
    tester = AuthTester()
    # Use an existing test user
    tester.run_all_tests('test@example.com', 'testpass123')
```

### Run the test:
```bash
pip install requests
python test_auth.py
```

---

## Expected Results After Fixes

### ✅ All Tests Should Pass:

1. **Unauthenticated Access**: 401 Unauthorized ✓
2. **User Login**: 200 OK with tokens ✓
3. **Authenticated Access**: 200 OK with data ✓
4. **Invalid Token**: 401 Unauthorized ✓
5. **Logout**: 200 OK with success message ✓
6. **Email Authentication**: Works without middleware issues ✓
7. **Item Ownership**: Users can only modify own items ✓
8. **Role-Based Access**: Staff/Admin have full access ✓

---

## Troubleshooting

### If Login Fails:
1. Verify user exists: `python manage.py shell` → `CustomUser.objects.filter(email='test@example.com')`
2. Check password: `user.check_password('password')`
3. Verify backend is loaded: `from django.conf import settings; print(settings.AUTHENTICATION_BACKENDS)`

### If Token Not Working:
1. Verify token is not expired (ACCESS_TOKEN_LIFETIME = 1 day)
2. Check token format (should be `Bearer <token>`)
3. Verify header is `Authorization` (not `auth` or `token`)

### If Permission Denied:
1. Check user role: `user.user_type`
2. Verify permission classes on view
3. Check ownership: Item should have `reporter` = current user

---

## Performance Considerations

The fixes add minimal overhead:
- Email backend: Direct lookup instead of middleware
- Permission checks: Simple field comparisons
- Token validation: Already handled by JWT

---

*All tests should complete successfully after these security fixes are applied!*
