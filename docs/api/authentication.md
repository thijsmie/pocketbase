# Authentication

User authentication and authorization features.

## RecordAuthService

::: pocketbase.services.record.RecordAuthService
    options:
      show_root_heading: true
      show_source: false

## Usage Examples

### Password Authentication

```python
from pocketbase import PocketBase

pb = PocketBase('http://localhost:8090')
users = pb.collection('users')

# Sign in with email and password
try:
    auth_result = await users.auth.with_password(
        'user@example.com', 
        'password123'
    )
    
    print(f"Logged in as: {auth_result['record']['email']}")
    print(f"Token: {auth_result['token']}")
    
    # The client is now authenticated for future requests
    current_user = auth_result['record']
    
except Exception as e:
    print(f"Login failed: {e}")
```

### User Registration

```python
# Create a new user account
try:
    new_user = await users.create({
        'email': 'newuser@example.com',
        'password': 'securepassword123',
        'passwordConfirm': 'securepassword123',
        'name': 'New User',
        'avatar': None  # Optional fields
    })
    
    print(f"User created: {new_user['email']}")
    
    # Automatically sign in after registration
    auth_result = await users.auth.with_password(
        'newuser@example.com',
        'securepassword123'
    )
    
except Exception as e:
    print(f"Registration failed: {e}")
```

### OAuth2 Authentication

```python
# First, get available auth methods
auth_methods = await users.auth.methods()

if auth_methods['oauth2']['enabled']:
    providers = auth_methods['oauth2']['providers']
    print("Available OAuth2 providers:")
    for provider in providers:
        print(f"- {provider['name']}")

# OAuth2 authentication (after user completes OAuth flow)
oauth_payload = {
    'provider': 'google',
    'code': 'oauth_authorization_code',
    'codeVerifier': 'code_verifier_from_pkce',
    'redirectUrl': 'http://localhost:3000/oauth/callback',
    'createData': {  # Optional data for new users
        'name': 'User Name'
    }
}

try:
    auth_result = await users.auth.with_oauth2(oauth_payload)
    print(f"OAuth2 login successful: {auth_result['record']['email']}")
except Exception as e:
    print(f"OAuth2 login failed: {e}")
```

### One-Time Password (OTP) Authentication

```python
# Request OTP to be sent via email
try:
    otp_result = await users.auth.request_otp('user@example.com')
    print(f"OTP sent! Use OTP ID: {otp_result['otpId']}")
    
    # User receives email with OTP code
    # Then authenticate with the OTP
    otp_code = input("Enter OTP code from email: ")
    
    auth_result = await users.auth.with_otp(
        otp_result['otpId'], 
        otp_code
    )
    
    print(f"OTP login successful: {auth_result['record']['email']}")
    
except Exception as e:
    print(f"OTP authentication failed: {e}")
```

### Token Refresh

```python
# Refresh the authentication token
try:
    refreshed_auth = await users.auth.refresh()
    print(f"Token refreshed for: {refreshed_auth['record']['email']}")
except Exception as e:
    print(f"Token refresh failed: {e}")
    # Might need to re-authenticate
```

### Admin Impersonation

```python
# Admin users can impersonate other users
pb = PocketBase('http://localhost:8090')

# First authenticate as admin
await pb.collection('_superusers').auth.with_password(
    'admin@example.com',
    'admin_password'
)

# Then impersonate a user (admin only)
try:
    impersonation_result = await users.auth.impersonate(
        'user_id_to_impersonate',
        duration=3600  # 1 hour in seconds
    )
    
    print(f"Now impersonating: {impersonation_result['record']['email']}")
    
except Exception as e:
    print(f"Impersonation failed: {e}")
```

## Authentication State Management

### Checking Authentication Status

```python
# Get the auth store
auth_store = pb._inners.auth

# Check if user is authenticated
if auth_store.is_valid():
    current_user = auth_store.model
    print(f"Authenticated as: {current_user['email']}")
    print(f"Token expires: {auth_store.token}")
else:
    print("Not authenticated")
```

### Manual Authentication State

```python
# Manually set authentication (if you have a token)
auth_store.set_token('your_jwt_token')

# Or set both token and user data
auth_data = {
    'token': 'your_jwt_token',
    'record': {
        'id': 'user_id',
        'email': 'user@example.com',
        # ... other user fields
    }
}
auth_store.set_user(auth_data)

# Clear authentication
auth_store.clear()
```

## Multi-Collection Authentication

Different collections can have different authentication methods:

```python
# Regular users collection
users = pb.collection('users')
await users.auth.with_password('user@example.com', 'password')

# Staff collection with different auth setup
staff = pb.collection('staff')
await staff.auth.with_password('staff@company.com', 'staff_password')

# Admin collection
admins = pb.collection('_superusers')
await admins.auth.with_password('admin@example.com', 'admin_password')
```

## Authentication Middleware Pattern

```python
from functools import wraps

def require_auth(func):
    """Decorator to ensure user is authenticated"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not pb._inners.auth.is_valid():
            raise Exception("Authentication required")
        return await func(*args, **kwargs)
    return wrapper

@require_auth
async def get_user_posts():
    current_user = pb._inners.auth.model
    return await pb.collection('posts').get_full_list({
        'filter': f'author = "{current_user["id"]}"'
    })
```

## Error Handling

```python
from pocketbase import PocketBaseError

async def safe_login(email: str, password: str):
    try:
        auth_result = await users.auth.with_password(email, password)
        return auth_result
    except PocketBaseError as e:
        if e.status == 400:
            print("Invalid email or password")
        elif e.status == 403:
            print("Account disabled or requires verification")
        else:
            print(f"Authentication error: {e}")
        return None
```

## Security Best Practices

### 1. Token Storage
```python
# In production, store tokens securely
import keyring

# Store token
auth_result = await users.auth.with_password(email, password)
keyring.set_password("myapp", "auth_token", auth_result['token'])

# Retrieve token
stored_token = keyring.get_password("myapp", "auth_token")
if stored_token:
    pb._inners.auth.set_token(stored_token)
```

### 2. Automatic Token Refresh
```python
import asyncio
from datetime import datetime, timedelta

async def auto_refresh_token():
    """Automatically refresh token before expiration"""
    while True:
        if pb._inners.auth.is_valid():
            try:
                await users.auth.refresh()
                print("Token refreshed successfully")
            except Exception as e:
                print(f"Token refresh failed: {e}")
                # Handle re-authentication
        
        # Wait before next refresh (adjust based on token lifetime)
        await asyncio.sleep(3600)  # 1 hour

# Run in background
asyncio.create_task(auto_refresh_token())
```

### 3. Logout Handling
```python
async def logout():
    """Properly logout user"""
    # Clear authentication state
    pb._inners.auth.clear()
    
    # Clear any stored tokens
    keyring.delete_password("myapp", "auth_token")
    
    print("Logged out successfully")
```
