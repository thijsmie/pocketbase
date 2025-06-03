import io
from pathlib import Path
from zipfile import ZipFile

import httpx

POCKETBASE_VERSION = "0.28.1"
POCKETBASE_PLATFORM = "linux_amd64"


def ensure_pocketbase_executable() -> Path:
    p = Path(__file__).parent / "executable" / f"pocketbase_{POCKETBASE_VERSION}_{POCKETBASE_PLATFORM}"
    if p.exists():
        return p / "pocketbase"

    print(
        "https://github.com/pocketbase/pocketbase"
        "/releases/download/"
        f"v{POCKETBASE_VERSION}"
        f"/pocketbase_{POCKETBASE_VERSION}_{POCKETBASE_PLATFORM}.zip"
    )

    resp = httpx.get(
        "https://github.com/pocketbase/pocketbase"
        "/releases/download/"
        f"v{POCKETBASE_VERSION}"
        f"/pocketbase_{POCKETBASE_VERSION}_{POCKETBASE_PLATFORM}.zip",
        follow_redirects=True,
    )
    p.mkdir(exist_ok=True, parents=True)
    zipfile = ZipFile(file=io.BytesIO(resp.content))
    zipfile.extract("pocketbase", p)
    exe = p / "pocketbase"
    exe.chmod(0o777)
    return exe
