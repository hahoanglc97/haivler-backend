import hashlib
import hmac
import time
from typing import Dict, Optional
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from .config import settings

class URLObfuscationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, secret_key: str = None):
        super().__init__(app)
        self.secret_key = secret_key or settings.SECRET_KEY
        self.url_mapping = self._generate_url_mapping()
        self.reverse_mapping = {v: k for k, v in self.url_mapping.items()}
    
    def _generate_url_mapping(self) -> Dict[str, str]:
        """Generate obfuscated URLs for API endpoints"""
        api_endpoints = [
            "/api/v1/auth/register",
            "/api/v1/auth/login", 
            "/api/v1/auth/logout",
            "/api/v1/users/me",
            "/api/v1/posts",
            "/api/v1/comments",
            "/api/v1/reactions"
        ]
        
        mapping = {}
        for endpoint in api_endpoints:
            # Create a hash-based obfuscated URL
            hash_input = f"{endpoint}:{self.secret_key}"
            endpoint_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:12]
            obfuscated_path = f"/api/x/{endpoint_hash}"
            mapping[endpoint] = obfuscated_path
            
        return mapping
    
    def _generate_time_based_token(self, path: str, timestamp: int) -> str:
        """Generate time-based access token for additional security"""
        message = f"{path}:{timestamp}"
        token = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()[:16]
        return token
    
    def _validate_time_token(self, path: str, token: str, timestamp: int) -> bool:
        """Validate time-based token (valid for 5 minutes)"""
        current_time = int(time.time())
        time_diff = current_time - timestamp
        
        # Token valid for 5 minutes
        if time_diff > 300 or time_diff < -60:
            return False
            
        expected_token = self._generate_time_based_token(path, timestamp)
        return hmac.compare_digest(token, expected_token)
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Skip middleware for docs, health, root, and system endpoints
        bypass_paths = ["/", "/health", "/docs", "/openapi.json", "/api/v1/system/"]
        if any(path.startswith(bp) for bp in bypass_paths) or path.startswith("/docs"):
            response = await call_next(request)
            return response
        
        # Check if this is an obfuscated URL request
        if path.startswith("/api/x/"):
            return await self._handle_obfuscated_request(request, call_next)
        
        # Check if this is a direct API call that should be blocked
        if path.startswith("/api/v1/"):
            return await self._handle_direct_api_request(request, path)
        
        # For all other requests, proceed normally
        response = await call_next(request)
        return response
    
    async def _handle_obfuscated_request(self, request: Request, call_next):
        """Handle requests to obfuscated URLs"""
        obfuscated_path = request.url.path
        
        # Debug logging
        print(f"Debug: Obfuscated path: {obfuscated_path}")
        print(f"Debug: Available mappings: {list(self.reverse_mapping.keys())}")
        
        # Find the real endpoint
        real_endpoint = self.reverse_mapping.get(obfuscated_path)
        if not real_endpoint:
            return JSONResponse(
                status_code=404,
                content={
                    "detail": "Endpoint not found",
                    "debug": {
                        "requested_path": obfuscated_path,
                        "available_paths": list(self.reverse_mapping.keys())
                    }
                }
            )
        
        print(f"Debug: Mapping {obfuscated_path} -> {real_endpoint}")
        
        # Check for time-based token in headers (optional additional security)
        x_timestamp = request.headers.get("X-Timestamp")
        x_token = request.headers.get("X-Access-Token")
        
        if x_timestamp and x_token:
            try:
                timestamp = int(x_timestamp)
                if not self._validate_time_token(obfuscated_path, x_token, timestamp):
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "Invalid access token"}
                    )
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid timestamp format"}
                )
        
        # Rewrite the request path to the real endpoint
        scope = request.scope.copy()
        scope["path"] = real_endpoint
        scope["raw_path"] = real_endpoint.encode()
        
        # Update the query string if present
        if request.url.query:
            scope["query_string"] = request.url.query.encode()
        
        # Create new request with modified path
        new_request = Request(scope, request.receive)
        
        response = await call_next(new_request)
        return response
    
    async def _handle_direct_api_request(self, request: Request, path: str):
        """Handle direct API requests - either redirect or block"""
        # Check if there's an obfuscated version of this endpoint
        obfuscated_url = self.url_mapping.get(path)
        
        if obfuscated_url:
            # Option 1: Redirect to obfuscated URL
            if request.method == "GET":
                return JSONResponse(
                    status_code=301,
                    content={"detail": f"Endpoint moved", "new_url": obfuscated_url},
                    headers={"Location": obfuscated_url}
                )
            else:
                # For non-GET requests, return the obfuscated URL info
                return JSONResponse(
                    status_code=308,
                    content={
                        "detail": "Use obfuscated endpoint",
                        "obfuscated_url": obfuscated_url,
                        "hint": "Add X-Timestamp and X-Access-Token headers for enhanced security"
                    }
                )
        
        # If no obfuscated version exists, return 404
        return JSONResponse(
            status_code=404,
            content={"detail": "Endpoint not found"}
        )
    
    def get_url_mapping(self) -> Dict[str, str]:
        """Get the current URL mapping for client reference"""
        return self.url_mapping.copy()
    
    def generate_access_token(self, obfuscated_path: str) -> Dict[str, str]:
        """Generate access token for a given obfuscated path"""
        timestamp = int(time.time())
        token = self._generate_time_based_token(obfuscated_path, timestamp)
        return {
            "timestamp": str(timestamp),
            "token": token,
            "expires_in": "300 seconds"
        }

class URLMappingResponse:
    """Helper class to provide URL mappings to authenticated clients"""
    
    def __init__(self, middleware: URLObfuscationMiddleware):
        self.middleware = middleware
    
    def get_endpoints(self) -> Dict[str, Dict[str, str]]:
        """Get all obfuscated endpoints with their details"""
        mappings = {}
        for real_url, obfuscated_url in self.middleware.get_url_mapping().items():
            mappings[real_url] = {
                "obfuscated_url": obfuscated_url,
                "access_info": self.middleware.generate_access_token(obfuscated_url)
            }
        return mappings