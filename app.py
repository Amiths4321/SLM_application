import shutil
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

from src.database import get_inspections, initialize_database, save_inspection
from src.intelligence.inspection_engine import WarehouseInspectionEngine
from src.intelligence.slm_inspector import analyze_inspection

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

engine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine
    initialize_database()
    engine = WarehouseInspectionEngine()
    yield


app = FastAPI(
    title="Warehouse Inspection Copilot API",
    version="1.0.0",
    lifespan=lifespan,
)


def save_upload_to_temp(file: UploadFile) -> Path:
    """Validate the upload and write it to a temporary file."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file name provided.")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG and PNG images are supported.",
        )

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        return Path(tmp.name)


@app.get("/")
def home():
    return {
        "message": "Warehouse Inspection API is running",
        "documentation": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/inspect")
async def inspect_image(file: UploadFile = File(...)):
    image_path = save_upload_to_temp(file)
    try:
        # engine.inspect is blocking, so keep it off the event loop
        result = await run_in_threadpool(engine.inspect, image_path)
        result["image"] = file.filename

        inspection_id = save_inspection(result)
        result["inspection_id"] = inspection_id
        return result
    finally:
        image_path.unlink(missing_ok=True)


@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    image_path = save_upload_to_temp(file)
    try:
        inspection = await run_in_threadpool(engine.inspect, image_path)
        inspection["image"] = file.filename

        report = await run_in_threadpool(analyze_inspection, inspection)
        inspection_id = save_inspection(inspection, report)

        return {
            "image": file.filename,
            "inspection_id": inspection_id,
            "inspection": inspection,
            "ai_analysis": report,
        }
    finally:
        image_path.unlink(missing_ok=True)


@app.get("/history")
def history(limit: int = 50):
    return get_inspections(limit)