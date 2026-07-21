from backend.app import create_app
from fastapi.testclient import TestClient

app = create_app()
client = TestClient(app)

def test_job_processing_endpoints() -> None:
    # Submit job
    response = client.post(
        "/api/v1/jobs/process-document",
        files={"file": ("test.txt", b"Hello world", "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    
    # In TestClient, BackgroundTasks run synchronously before returning the response.
    # Therefore, the job should be COMPLETED immediately.
    assert data["status"] in ("pending", "running", "completed") 
    
    job_id = data["job_id"]
    
    # Get job status
    res2 = client.get(f"/api/v1/jobs/{job_id}")
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["job_id"] == job_id
    assert d2["status"] == "completed"
    assert d2["progress"] == 100

def test_job_not_found() -> None:
    res = client.get("/api/v1/jobs/invalid-id")
    assert res.status_code == 404
