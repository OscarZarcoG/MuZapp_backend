import requests
import json

def test_login():
    url = 'http://localhost:8000/api/user/login/'
    data = {
        'username': 'daniel',
        'password': 'dasher123'
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Content: {response.text}")
        
        if response.status_code == 500:
            print("\nError 500 - Internal Server Error detected")
            
    except Exception as e:
        print(f"Error making request: {e}")

if __name__ == '__main__':
    test_login()