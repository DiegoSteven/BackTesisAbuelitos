import requests
import json

base_url = "http://localhost:5000"

endpoints = [
    "/admin/train-sessions",
    "/admin/paseo-sessions",
    "/admin/abecedario-sessions"
]

for endpoint in endpoints:
    print(f"--- FETCHING {endpoint} ---")
    try:
        response = requests.get(f"{base_url}{endpoint}")
        if response.status_code == 200:
            data = response.json()
            # Print first 2 items of sessions to check structure
            if 'sessions' in data and len(data['sessions']) > 0:
                print(json.dumps(data['sessions'][:2], indent=2))
            else:
                print("No sessions found or empty list.")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Exception: {e}")
    print("\n")
