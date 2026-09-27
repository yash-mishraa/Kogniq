import asyncio
import sys

import httpx


async def main() -> None:
    base_url = "http://127.0.0.1:8000"
    
    async with httpx.AsyncClient(base_url=base_url) as client:
        # Verify server is up
        try:
            resp = await client.get("/")
            if resp.status_code != 200:
                print("Server not ready")
                sys.exit(1)
        except Exception:
            print("Server not running")
            sys.exit(1)

        # We will write specific test cases as pytest instead, and run them against the live server.
        print("Harness ready")
        
if __name__ == "__main__":
    asyncio.run(main())
