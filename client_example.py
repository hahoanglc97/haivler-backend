#!/usr/bin/env python3
"""
Example client for using obfuscated API endpoints
This script demonstrates how to interact with the hidden/obfuscated backend URLs
"""

import requests
import json
import time
from typing import Dict, Optional

class HaivlerObfuscatedClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.endpoints = {}
        
    def login(self, username: str, password: str) -> bool:
        """Login to get JWT token"""
        try:
            # First try direct login (this might be redirected)
            login_data = {"username": username, "password": password}
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                data=login_data
            )
            
            if response.status_code == 308:
                # Use obfuscated endpoint
                obfuscated_url = response.json().get("obfuscated_url")
                if obfuscated_url:
                    response = requests.post(
                        f"{self.base_url}{obfuscated_url}",
                        data=login_data
                    )
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data["access_token"]
                print(f"✅ Login successful")
                return True
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def get_obfuscated_endpoints(self) -> Dict:
        """Get all obfuscated endpoint mappings"""
        if not self.token:
            print("❌ Please login first")
            return {}
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/system/endpoints",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.endpoints = data["endpoints"]
                print(f"✅ Retrieved {len(self.endpoints)} obfuscated endpoints")
                return data
            else:
                print(f"❌ Failed to get endpoints: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Error getting endpoints: {str(e)}")
            return {}
    
    def make_obfuscated_request(self, original_endpoint: str, method: str = "GET", 
                               data: Optional[Dict] = None, 
                               use_time_token: bool = True) -> Optional[requests.Response]:
        """Make a request to an obfuscated endpoint"""
        if not self.token:
            print("❌ Please login first")
            return None
            
        if not self.endpoints:
            print("📡 Getting obfuscated endpoints...")
            self.get_obfuscated_endpoints()
        
        endpoint_info = self.endpoints.get(original_endpoint)
        if not endpoint_info:
            print(f"❌ No obfuscated endpoint found for {original_endpoint}")
            return None
        
        obfuscated_url = endpoint_info["obfuscated_url"]
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Add time-based security headers if requested
        if use_time_token:
            access_info = endpoint_info["access_info"]
            headers.update({
                "X-Timestamp": access_info["timestamp"],
                "X-Access-Token": access_info["token"]
            })
        
        try:
            url = f"{self.base_url}{obfuscated_url}"
            
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                print(f"❌ Unsupported method: {method}")
                return None
            
            print(f"✅ {method} {obfuscated_url} -> {response.status_code}")
            return response
            
        except Exception as e:
            print(f"❌ Request error: {str(e)}")
            return None
    
    def demonstrate_usage(self):
        """Demonstrate the obfuscated API usage"""
        print("🔒 Haivler Obfuscated API Client Demo")
        print("=" * 50)
        
        # Show endpoint mappings
        if self.endpoints:
            print("\n📋 Available Obfuscated Endpoints:")
            for original, info in self.endpoints.items():
                print(f"  {original} -> {info['obfuscated_url']}")
        
        print("\n🧪 Testing obfuscated endpoints...")
        
        # Test user profile endpoint
        response = self.make_obfuscated_request("/api/v1/users/me")
        if response and response.status_code == 200:
            user_data = response.json()
            print(f"👤 User: {user_data.get('username', 'Unknown')}")
        
        # Test posts endpoint
        response = self.make_obfuscated_request("/api/v1/posts")
        if response and response.status_code == 200:
            posts = response.json()
            print(f"📄 Found {len(posts)} posts")
        
        print("\n✨ Demo completed!")

def main():
    """Main demo function"""
    client = HaivlerObfuscatedClient()
    
    print("Please login to continue:")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    
    if client.login(username, password):
        client.get_obfuscated_endpoints()
        client.demonstrate_usage()
    else:
        print("❌ Login failed. Please check your credentials.")

if __name__ == "__main__":
    main()