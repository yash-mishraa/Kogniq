import sys
from pathlib import Path

import uvicorn

# Ensure all workspace packages are resolvable when run directly
root_dir = Path(__file__).parent.parent
for pkg_dir in (root_dir / "packages").iterdir():
    if pkg_dir.is_dir() and (pkg_dir / "src").exists():
        sys.path.insert(0, str(pkg_dir / "src"))

from backend.core.settings import settings  # noqa: E402

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
