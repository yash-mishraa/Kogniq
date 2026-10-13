import requests
session = requests.Session()
resp = session.post("http://127.0.0.1:8000/api/v1/auth/login", json={"email": "admin@kogniq.ai", "password": "password"})
print(resp.json())
