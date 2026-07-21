import asyncio
import sys
from pathlib import Path

# Ensure all workspace packages are resolvable when run directly
root_dir = Path(__file__).parent.parent
for pkg_dir in (root_dir / "packages").iterdir():
    if pkg_dir.is_dir() and (pkg_dir / "src").exists():
        sys.path.insert(0, str(pkg_dir / "src"))

import json  # noqa: E402
from threading import Thread  # noqa: E402

import httpx  # noqa: E402
import uvicorn  # noqa: E402
from backend.app import create_app  # noqa: E402
from backend.core.settings import settings  # noqa: E402


def start_server() -> None:
    uvicorn.run(create_app(), host=settings.host, port=settings.port, log_level="warning")


async def run_demo() -> None:
    print(f"[{'Demo':<10}] Waiting for backend to start...")
    await asyncio.sleep(2)

    url = f"http://{settings.host}:{settings.port}/api/v1/learning/generate"

    request_data = {"document_id": "demo-doc-777", "generator": "flashcards", "options": {}}

    print(f"[{'Demo':<10}] Sending POST {url}")
    print(f"[{'Demo':<10}] Payload: {json.dumps(request_data)}")

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=request_data)

    print(f"[{'Demo':<10}] Received HTTP {response.status_code}")
    print(f"[{'Demo':<10}] Response JSON:\n")
    print(json.dumps(response.json(), indent=2))

    sys.exit(0)


if __name__ == "__main__":
    t = Thread(target=start_server, daemon=True)
    t.start()
    asyncio.run(run_demo())
