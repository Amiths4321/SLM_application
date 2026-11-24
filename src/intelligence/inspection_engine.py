
import json
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone

from src.vision.object_detector import WarehouseObjectDetector
from src.ocr.text_extractor import WarehouseOCR


class WarehouseInspectionEngine:

    def __init__(self):
        print("Initializing warehouse inspection engine...")

        self.detector = WarehouseObjectDetector()
        self.ocr = WarehouseOCR()

        self.output_dir = Path("data/processed/inspections")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print("Inspection engine ready.")

    def inspect(self, image_path):

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(image_path)

        print("\nRunning YOLO object detection...")
        detection_result = self.detector.detect(image_path)

        print("Running PaddleOCR...")
        ocr_result = self.ocr.extract_text(image_path)

        object_counts = Counter(
            item["object"]
            for item in detection_result["detections"]
        )

        inspection = {
            "image": image_path.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "object_detection": {
                "total_objects": detection_result["total_objects"],
                "object_counts": dict(object_counts),
                "detections": detection_result["detections"],
                "annotated_image": detection_result["annotated_image"]
            },
            "ocr": {
                "total_text_regions": len(ocr_result),
                "extracted_text": ocr_result
            }
        }

        output_path = self.output_dir / f"{image_path.stem}_inspection.json"

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(inspection, file, indent=4, ensure_ascii=False)

        inspection["report_path"] = str(output_path)

        return inspection


if __name__ == "__main__":

    engine = WarehouseInspectionEngine()

    image_path = input(
        "\nEnter warehouse image or shipping label path: "
    ).strip().strip('"')

    result = engine.inspect(image_path)

    print("\n" + "=" * 50)
    print("WAREHOUSE INSPECTION REPORT")
    print("=" * 50)

    print("\nImage:", result["image"])

    print("\nDetected Objects:")
    print(result["object_detection"]["object_counts"])

    print("\nExtracted Text:")
    for item in result["ocr"]["extracted_text"]:
        print(
            f"{item['text']} "
            f"(confidence: {item['confidence']})"
        )

    print("\nJSON Report:", result["report_path"])
