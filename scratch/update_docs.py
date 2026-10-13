import requests
import json
session = requests.Session()
resp = session.post("http://127.0.0.1:8000/api/v1/auth/login", json={"email": "admin@kogniq.ai", "password": "password"})
user_id = session.cookies.get("kogniq_auth")
print(user_id)
