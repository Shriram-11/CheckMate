import requests
import time

# Define the API endpoint
url = "https://checkmate-lmc4.onrender.com/api/entrysystem/health_check/"

# Function to check the health of the API


def check_health():
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"API Response: {data['message']}")
        else:
            print(f"Failed to reach API. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


# Call the API every 30 seconds
while True:
    check_health()
    time.sleep(50)  # wait for 30 seconds
