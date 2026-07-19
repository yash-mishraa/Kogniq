import sys
from pathlib import Path

import uvicorn

# Ensure the workspace packages are resolvable when run directly
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "shared" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "backend" / "src"))

from backend.core.settings import settings

if __name__ == "__main__":
    print(
        f"Launching {settings.app_name} on {settings.host}:{settings.port} ({settings.environment})"
    )

    uvicorn.run(
        "backend.app:create_app",
        factory=True,
        host=settings.host,
        port=settings.port,
        reload=True,
    )
