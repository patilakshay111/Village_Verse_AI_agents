import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BACKEND_ROOT = Path(__file__).resolve().parent
VILLAGE_ROOT = BACKEND_ROOT.parent
FRONTEND_DIST = VILLAGE_ROOT / "frontend" / "dist"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.api import api_router  # noqa: E402
from app.database.base import init_db  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="VillageVerse API",
    description="Multi-agent Indian village simulation",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "VillageVerse"}


def _mount_frontend() -> bool:
    index = FRONTEND_DIST / "index.html"
    if not index.is_file():
        return False

    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend-assets")

    @app.get("/")
    def serve_home():
        return FileResponse(index)

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        reserved = ("docs", "openapi.json", "redoc")
        if full_path in reserved or full_path.startswith("docs"):
            raise HTTPException(status_code=404, detail="Not found")
        target = FRONTEND_DIST / full_path
        if target.is_file():
            return FileResponse(target)
        return FileResponse(index)

    return True


UI_ENABLED = _mount_frontend()
