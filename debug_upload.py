"""
Test script to debug the upload functionality
"""
import requests
import os

def test_upload():
    """Test file upload to the API"""
    
    # Test with a simple text file first
    test_file_path = "test_document.txt"
    
    if not os.path.exists(test_file_path):
        print("❌ Test file not found")
        return
    
    url = "http://localhost:5000/api/upload"
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': (test_file_path, f, 'text/plain')}
            response = requests.post(url, files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                json_response = response.json()
                print(f"JSON Response: {json_response}")
            except Exception as e:
                print(f"Failed to parse JSON: {e}")
        
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_upload()
