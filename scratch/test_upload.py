import requests
import json
import time
import sys

s = requests.Session()
r = s.post("http://127.0.0.1:8000/api/v1/auth/login", json={"email": "admin@kogniq.ai", "password": "password"})
print("Login:", r.status_code)
sys.stdout.flush()

with open("sample_paper.pdf", "rb") as f:
    files = {"file": ("sample_paper.pdf", f, "application/pdf")}
    r = s.post("http://127.0.0.1:8000/api/v1/documents/process", files=files)
    print("Upload:", r.status_code, r.text)
    sys.stdout.flush()
    doc_id = r.json()["document_id"]

print("Polling status...")
sys.stdout.flush()
for _ in range(60):
    r = s.get("http://127.0.0.1:8000/api/v1/documents")
    docs = r.json()
    doc = next((d for d in docs if d["id"] == doc_id), None)
    print(f"Status: {doc['status'] if doc else 'Not found'}")
    sys.stdout.flush()
    if doc and doc["status"] == "Ready":
        break
    if doc and doc["status"] == "Failed":
        print("Failed processing!")
        sys.exit(1)
    time.sleep(2)

print("\nFetching learning materials...")
r = s.get(f"http://127.0.0.1:8000/api/v1/learning/{doc_id}")
print("Learning:", r.status_code)
sys.stdout.flush()
print(json.dumps(r.json(), indent=2)[:500])
sys.stdout.flush()

