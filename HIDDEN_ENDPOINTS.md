# Hidden/Obfuscated Endpoint System

This system provides URL obfuscation for enhanced API security by hiding the actual endpoint paths from potential attackers.

## How It Works

### 1. URL Obfuscation
- All main API endpoints are mapped to obfuscated URLs using SHA256 hashing
- Original endpoints like `/api/v1/auth/login` become `/api/x/9592fc5373e2`
- The mapping is consistent but unpredictable without the secret key

### 2. Access Control
- **Direct API Access**: Blocked with redirection info to obfuscated URLs
- **Obfuscated Access**: Allowed with proper authentication
- **System Endpoints**: Bypass the middleware for internal operations

## Current Obfuscated Endpoints

| Original Endpoint | Obfuscated URL | Purpose |
|------------------|----------------|---------|
| `/api/v1/auth/register` | `/api/x/1f217a698b25` | User registration |
| `/api/v1/auth/login` | `/api/x/9592fc5373e2` | User login |
| `/api/v1/users/me` | `/api/x/5baaf1c55a0a` | User profile |
| `/api/v1/posts` | `/api/x/ff0d498c575b` | Posts CRUD |
| `/api/v1/comments` | `/api/x/0ebcf2cda524` | Comments |
| `/api/v1/reactions` | `/api/x/7e7cc3288efb` | Reactions |

## Usage Examples

### 1. User Registration (Obfuscated)
```bash
curl -X POST "http://localhost:8000/api/x/1f217a698b25" \
  -H "Content-Type: application/json" \
  -d '{"username":"user","email":"user@example.com","password":"password123"}'
```

### 2. User Login (Obfuscated)
```bash
curl -X POST "http://localhost:8000/api/x/9592fc5373e2" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user&password=password123"
```

### 3. Access User Profile (Obfuscated + Auth)
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "http://localhost:8000/api/x/5baaf1c55a0a"
```

### 4. Get Endpoint Mappings (For Authenticated Users)
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "http://localhost:8000/api/v1/system/endpoints"
```

## Direct API Access (Blocked)

Attempting to access original endpoints will return redirection information:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login"
# Returns: {"detail":"Use obfuscated endpoint","obfuscated_url":"/api/x/9592fc5373e2"}
```

## Enhanced Security Features

### 1. Time-Based Access Tokens (Optional)
For additional security, you can use time-based access tokens:

```bash
# Get access token for an endpoint
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "http://localhost:8000/api/v1/system/token/1f217a698b25"

# Use with headers
curl -X POST "http://localhost:8000/api/x/1f217a698b25" \
  -H "X-Timestamp: 1641234567" \
  -H "X-Access-Token: abc123def456" \
  -H "Content-Type: application/json" \
  -d '{"username":"user","email":"user@example.com","password":"password123"}'
```

### 2. Client Helper Script
Use the provided `client_example.py` for automated obfuscated API interaction:

```bash
python3 client_example.py
```

## Security Benefits

1. **Endpoint Discovery Prevention**: Attackers cannot easily discover API endpoints
2. **Reduced Attack Surface**: Direct endpoint access is blocked
3. **Consistent Authentication**: All obfuscated endpoints require proper auth
4. **Time-Based Security**: Optional expiring access tokens
5. **Audit Trail**: All access attempts are logged

## Configuration

The obfuscation is based on the `SECRET_KEY` in your environment. To regenerate mappings:
1. Change the `SECRET_KEY` 
2. Restart the application
3. Update client applications with new mappings

## Client Integration

### Python Client Example
```python
import requests

class HaivlerClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        
    def login(self, username, password):
        response = requests.post(
            f"{self.base_url}/api/x/9592fc5373e2",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            return True
        return False
    
    def get_profile(self):
        if not self.token:
            return None
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(
            f"{self.base_url}/api/x/5baaf1c55a0a",
            headers=headers
        )
        return response.json() if response.status_code == 200 else None
```

### JavaScript Client Example
```javascript
class HaivlerClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
        this.token = null;
    }
    
    async login(username, password) {
        const response = await fetch(`${this.baseUrl}/api/x/9592fc5373e2`, {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: `username=${username}&password=${password}`
        });
        
        if (response.ok) {
            const data = await response.json();
            this.token = data.access_token;
            return true;
        }
        return false;
    }
    
    async getProfile() {
        if (!this.token) return null;
        
        const response = await fetch(`${this.baseUrl}/api/x/5baaf1c55a0a`, {
            headers: {'Authorization': `Bearer ${this.token}`}
        });
        
        return response.ok ? await response.json() : null;
    }
}
```

## Monitoring and Debugging

- All requests are logged with their original and obfuscated paths
- Failed access attempts are recorded
- System endpoints provide mapping information for authenticated users
- Debug mode can be enabled for troubleshooting

## Notes

- The middleware preserves all FastAPI features (validation, documentation, etc.)
- Obfuscated URLs are stable across application restarts (same secret = same URLs)
- System endpoints (`/api/v1/system/*`) bypass obfuscation for management
- Health check and documentation endpoints remain accessible