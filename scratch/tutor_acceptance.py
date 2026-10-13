import requests

def main():
    session = requests.Session()
    # Login
    resp = session.post("http://127.0.0.1:8000/api/v1/auth/login", json={"email": "admin@kogniq.ai", "password": "password"})
    print("Login:", resp.status_code)
    
    doc_id = "a2c5d03a-b167-4f7f-9730-afef5d389a96"
    print(f"Using Document ID: {doc_id}")
    
    # 1. Factual question
    print("\n--- TUTOR: Factual Question ---")
    resp = session.post(f"http://127.0.0.1:8000/api/v1/agent/tutor/chat", json={
        "document_id": doc_id,
        "messages": [{"role": "user", "content": "Who is the speaker of this address and who are they addressing?"}],
    })
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Content: {data.get('content', '')[:200].replace(chr(10), ' ')}")
        print(f"Events: {data.get('tool_events', [])}")
    else:
        print(resp.text)

    # 2. Conceptual question
    print("\n--- TUTOR: Conceptual Question ---")
    resp = session.post(f"http://127.0.0.1:8000/api/v1/agent/tutor/chat", json={
        "document_id": doc_id,
        "messages": [{"role": "user", "content": "What is the main economic thesis presented in the document?"}],
    })
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Content: {data.get('content', '')[:200].replace(chr(10), ' ')}")
        print(f"Events: {data.get('tool_events', [])}")
    else:
        print(resp.text)

    # 3. Retrieval question
    print("\n--- TUTOR: Retrieval Question ---")
    resp = session.post(f"http://127.0.0.1:8000/api/v1/agent/tutor/chat", json={
        "document_id": doc_id,
        "messages": [{"role": "user", "content": "Can you search the document for any mention of the Bipartisan Infrastructure Law and explain its impact?"}],
    })
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Content: {data.get('content', '')[:200].replace(chr(10), ' ')}")
        print(f"Events: {data.get('tool_events', [])}")
    else:
        print(resp.text)

main()
