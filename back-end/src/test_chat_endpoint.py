
import requests
import json
import time

API_CHAT = "http://localhost:8000/api/v1/chat"

def test_chat():
    payload = {
        "message": "hello",
        "agent_types": ["rag"],
        "use_image": False
    }
    
    print(f"Sending request to {API_CHAT}...")
    start_time = time.time()
    try:
        response = requests.post(API_CHAT, json=payload, timeout=60)
        duration = time.time() - start_time
        print(f"Status Code: {response.status_code}")
        print(f"Duration: {duration:.2f}s")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_chat()
