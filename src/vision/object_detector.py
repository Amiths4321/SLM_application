
from pathlib import Path
from ultralytics import YOLO

MODEL_PATH = "yolo26n.pt"

OUTPUT_DIR = Path("data/processed/detections")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class WarehouseObjectDetector:

    def __init__(self):
        print("Loading YOLO26 model...")
        self.model = YOLO(MODEL_PATH)
        print("YOLO26 loaded successfully.")

    def detect(self, image_path, confidence=0.35):
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        results = self.model.predict(
            source=str(image_path),
            conf=confidence,
            save=False,
            verbose=False
        )

        detections = []

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence_score = float(box.conf[0])
                coordinates = box.xyxy[0].tolist()

                detections.append({
                    "object": self.model.names[class_id],
                    "class_id": class_id,
                    "confidence": round(confidence_score, 4),
                    "bbox": [round(x, 2) for x in coordinates]
                })

            output_path = OUTPUT_DIR / image_path.name
            result.save(filename=str(output_path))

        return {
            "image": image_path.name,
            "total_objects": len(detections),
            "detections": detections,
            "annotated_image": str(output_path)
        }


if __name__ == "__main__":
    detector = WarehouseObjectDetector()

    image_path = input("Enter warehouse image path: ").strip().strip('"')

    result = detector.detect(image_path)

    print("\nDetection Results")
    print("=" * 40)
    print("Image:", result["image"])
    print("Objects detected:", result["total_objects"])

    for item in result["detections"]:
        print(
            item["object"],
            "| Confidence:", item["confidence"],
            "| Bounding box:", item["bbox"]
        )

    print("\nAnnotated image:", result["annotated_image"])
