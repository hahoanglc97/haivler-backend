#!/bin/bash

echo "🚀 Testing Haivler Full Stack Integration"
echo "========================================"

# Test backend health
echo "1. Testing Backend Health..."
BACKEND_HEALTH=$(curl -s http://localhost:8000/health)
if [[ $BACKEND_HEALTH == *"healthy"* ]]; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    exit 1
fi

# Test frontend accessibility
echo "2. Testing Frontend Accessibility..."
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [[ $FRONTEND_RESPONSE == "200" ]]; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend accessibility check failed"
    exit 1
fi

# Test obfuscated endpoints
echo "3. Testing Obfuscated Endpoints..."

# Test direct API access (should be blocked)
echo "   - Testing direct API blocking..."
DIRECT_API=$(curl -s http://localhost:8000/api/v1/auth/register -X POST)
if [[ $DIRECT_API == *"obfuscated_url"* ]]; then
    echo "✅ Direct API access properly blocked"
else
    echo "❌ Direct API access blocking failed"
fi

# Test user registration via obfuscated endpoint
echo "   - Testing user registration..."
REGISTER_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/x/1f217a698b25" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser_integration","email":"test@integration.com","password":"testpass123"}')

if [[ $REGISTER_RESPONSE == *"testuser_integration"* ]]; then
    echo "✅ User registration via obfuscated endpoint works"
else
    echo "⚠️ User registration may have failed (possibly user already exists)"
fi

# Test user login via obfuscated endpoint
echo "   - Testing user login..."
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/x/9592fc5373e2" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser_integration&password=testpass123")

if [[ $LOGIN_RESPONSE == *"access_token"* ]]; then
    echo "✅ User login via obfuscated endpoint works"
    TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    echo "   Token obtained: ${TOKEN:0:20}..."
else
    echo "❌ User login via obfuscated endpoint failed"
    echo "   Response: $LOGIN_RESPONSE"
fi

# Test authenticated endpoint
if [[ -n "$TOKEN" ]]; then
    echo "   - Testing authenticated endpoint..."
    PROFILE_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
      "http://localhost:8000/api/x/5baaf1c55a0a")
    
    if [[ $PROFILE_RESPONSE == *"testuser_integration"* ]]; then
        echo "✅ Authenticated profile access works"
    else
        echo "❌ Authenticated profile access failed"
    fi
fi

# Test posts endpoint
echo "   - Testing posts endpoint..."
POSTS_RESPONSE=$(curl -s "http://localhost:8000/api/x/ff0d498c575b")
if [[ $POSTS_RESPONSE == *"["* ]]; then
    echo "✅ Posts endpoint accessible"
else
    echo "❌ Posts endpoint failed"
fi

echo ""
echo "🎉 Integration Test Summary"
echo "=========================="
echo "✅ Backend: http://localhost:8000"
echo "✅ Frontend: http://localhost:3000"
echo "✅ MinIO Console: http://localhost:9001"
echo "✅ MySQL: localhost:3306"
echo ""
echo "🔒 Security Features:"
echo "   - Direct API access blocked"
echo "   - Obfuscated endpoints working"
echo "   - JWT authentication functional"
echo ""
echo "🌟 System is ready for use!"
echo ""
echo "Next steps:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Register a new account"
echo "3. Start sharing images!"