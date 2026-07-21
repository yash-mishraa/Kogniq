import sys
import time
from pathlib import Path
from threading import Thread

import httpx
import uvicorn

root = Path(__file__).resolve().parent.parent
for pkg_dir in (root / "packages").iterdir():
    if pkg_dir.is_dir() and (pkg_dir / "src").exists():
        sys.path.insert(0, str(pkg_dir / "src"))

from backend.app import create_app  # noqa: E402


def start_server() -> None:
    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=8002, log_level="error")


def main() -> None:
    print("Starting backend server for Jobs API Demo...")
    server_thread = Thread(target=start_server, daemon=True)
    server_thread.start()

    # Wait for server to boot
    time.sleep(2)

    demo_doc = (
        "This is a demo document. "
        "It will be uploaded asynchronously and processed in the background."
    )

    try:
        print("\n--- 1. Submitting Document ---")
        files = {"file": ("demo_jobs.md", demo_doc.encode("utf-8"), "text/markdown")}
        response = httpx.post(
            "http://127.0.0.1:8002/api/v1/jobs/process-document", files=files, timeout=30.0
        )
        response.raise_for_status()

        result = response.json()
        job_id = result["job_id"]
        status = result["status"]
        print(f"Job submitted successfully. ID: {job_id} | Status: {status}")

        print("\n--- 2. Polling Job Status ---")

        for _ in range(10):
            res = httpx.get(f"http://127.0.0.1:8002/api/v1/jobs/{job_id}")
            res.raise_for_status()
            data = res.json()

            print(
                f"Status: {data['status']:>10} | Progress: {data['progress']:>3}% | "
                f"Message: {data['message']}"
            )

            if data["status"] in ("completed", "failed", "cancelled"):
                break

            time.sleep(1)

        print("\nDemo finished.")
    except Exception as e:
        print(f"An error occurred during demo: {e}")


if __name__ == "__main__":
    main()
