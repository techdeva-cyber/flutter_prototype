import requests
import json

# Base URL for our API
BASE_URL = "http://localhost:8000/api"

def test_api_endpoints():
    print("Testing SmartAttend API endpoints...")
    
    # Test 1: Register a new user
    print("\n1. Testing user registration...")
    register_data = {
        "username": "teststudent",
        "email": "test@student.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "Student",
        "role": "student",
        "semester": "3rd",
        "course": "Computer Science",
        "section": "A"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
        print(f"Registration response status: {response.status_code}")
        if response.status_code == 201:
            print("✓ User registration successful")
            user_data = response.json()
            token = user_data['token']
            print(f"Auth token: {token[:10]}...")
        else:
            print(f"✗ Registration failed: {response.text}")
    except Exception as e:
        print(f"✗ Registration error: {e}")
    
    # Test 2: Login
    print("\n2. Testing user login...")
    login_data = {
        "email": "test@student.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        print(f"Login response status: {response.status_code}")
        if response.status_code == 200:
            print("✓ User login successful")
            login_data = response.json()
            token = login_data['token']
            print(f"Auth token: {token[:10]}...")
        else:
            print(f"✗ Login failed: {response.text}")
    except Exception as e:
        print(f"✗ Login error: {e}")
    
    # Test 3: Get user profile
    print("\n3. Testing user profile retrieval...")
    headers = {
        "Authorization": f"Token {token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
        print(f"Profile response status: {response.status_code}")
        if response.status_code == 200:
            print("✓ User profile retrieval successful")
            profile_data = response.json()
            print(f"User: {profile_data['first_name']} {profile_data['last_name']}")
        else:
            print(f"✗ Profile retrieval failed: {response.text}")
    except Exception as e:
        print(f"✗ Profile retrieval error: {e}")
    
    print("\nAPI testing completed.")

if __name__ == "__main__":
    test_api_endpoints()