import requests
import sys

base_url = "http://127.0.0.1:8000"

# Register
print("Registering...")
resp = requests.post(f"{base_url}/api/auth/register", json={
    "name": "TestPredict",
    "email": "testpredict@example.com",
    "password": "password123",
    "age": 25
})
print(resp.status_code, resp.text)

# Login
print("Logging in...")
resp = requests.post(f"{base_url}/api/auth/login", data={
    "username": "testpredict@example.com",
    "password": "password123"
})
print(resp.status_code, resp.text)
if resp.status_code != 200:
    sys.exit(1)
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Predict
print("Predicting...")
# We need a dummy image
from PIL import Image
import io
img = Image.new('RGB', (100, 100), color = 'red')
img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='JPEG')
image_bytes = img_byte_arr.getvalue()

files = {'file': ('dummy.jpg', image_bytes, 'image/jpeg')}
resp = requests.post(f"{base_url}/api/scan/predict", headers=headers, files=files)
print(resp.status_code)
print(resp.text)
