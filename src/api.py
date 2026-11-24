
from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
import tempfile
import shutil

from src.intelligence.inspection_engine import WarehouseInspectionEngine
from src.intelligence.slm_inspector import analyze_inspection
from src.database import (
    initialize_database,
    save_inspection,
    get_inspections,
    get_inspection_by_id
)

app = FastAPI(
    title="Warehouse Inspection Copilot API",
    description="YOLO26, PaddleOCR and Qwen-powered warehouse inspection",
    version="1.0.0"
)

engine = None


@app.on_event("startup")
def startup():
    global engine
    initialize_database()
    engine = WarehouseInspectionEngine()


@app.get("/")
def home():
    return {
        "message": "Warehouse Inspection API is running",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/inspect")
async def inspect_image(file: UploadFile = File(...)):
    if Path(file.filename).suffix.lower() not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(400, "Only JPG and PNG images are supported")

    image_path = None

    try:
        suffix = Path(file.filename).suffix.lower()

        with tempfile.NamedTemporaryFile(
            suffix=suffix, delete=False
        ) as temp:
            shutil.copyfileobj(file.file, temp)
            image_path = Path(temp.name)

        result = engine.inspect(image_path)
        result["image"] = file.filename

        inspection_id = save_inspection(result)

        return {
            "inspection_id": inspection_id,
            "inspection": result
        }

    finally:
        if image_path and image_path.exists():
            image_path.unlink()


@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    if Path(file.filename).suffix.lower() not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(400, "Only JPG and PNG images are supported")

    image_path = None

    try:
        suffix = Path(file.filename).suffix.lower()

        with tempfile.NamedTemporaryFile(
            suffix=suffix, delete=False
        ) as temp:
            shutil.copyfileobj(file.file, temp)
            image_path = Path(temp.name)

        inspection = engine.inspect(image_path)
        inspection["image"] = file.filename

        report = analyze_inspection(inspection)

        inspection_id = save_inspection(inspection, report)

        return {
            "inspection_id": inspection_id,
            "inspection": inspection,
            "ai_analysis": report
        }

    finally:
        if image_path and image_path.exists():
            image_path.unlink()


@app.get("/history")
def inspection_history():
    return {"inspections": get_inspections(50)}


@app.get("/history/{inspection_id}")
def inspection_details(inspection_id: int):
    result = get_inspection_by_id(inspection_id)

    if result is None:
        raise HTTPException(404, "Inspection not found")

    return result
